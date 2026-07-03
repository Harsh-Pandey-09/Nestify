import os
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.dependencies import require_owner, require_tenant, get_current_user
from app.models.user import User
from app.models.listing import Listing, ListingStatus, RoomType, FurnishingStatus
from app.models.tenant_profile import TenantProfile
from app.schemas.listing import (
    ListingCreateRequest,
    ListingUpdateRequest,
    ListingResponse,
    ListingWithScoreResponse,
    PaginatedListingsResponse,
)
from app.schemas.common import MessageResponse
from app.services import listing_service, compatibility_service, notification_service
from app.utils.validators import validate_image_file
from app.utils.helpers import generate_unique_filename, ensure_dir

router = APIRouter(prefix="/api/listings", tags=["Listings"])


# ---------- Owner: create / manage listings ----------

@router.post("", response_model=ListingResponse, status_code=201)
def create_listing(
    payload: ListingCreateRequest, db: Session = Depends(get_db), current_user: User = Depends(require_owner)
):
    listing = Listing(owner_id=current_user.id, **payload.model_dump())
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return ListingResponse.from_orm_with_photos(listing)


@router.get("/owner/mine", response_model=List[ListingResponse])
def get_my_listings(db: Session = Depends(get_db), current_user: User = Depends(require_owner)):
    listings = db.query(Listing).filter(Listing.owner_id == current_user.id).order_by(Listing.created_at.desc()).all()
    return [ListingResponse.from_orm_with_photos(l) for l in listings]


@router.get("/{listing_id}", response_model=ListingResponse)
def get_listing(listing_id: int, db: Session = Depends(get_db)):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
    return ListingResponse.from_orm_with_photos(listing)


@router.put("/{listing_id}", response_model=ListingResponse)
def update_listing(
    listing_id: int,
    payload: ListingUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_owner),
):
    listing = db.query(Listing).filter(Listing.id == listing_id, Listing.owner_id == current_user.id).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(listing, field, value)

    db.commit()
    db.refresh(listing)
    return ListingResponse.from_orm_with_photos(listing)


@router.delete("/{listing_id}", response_model=MessageResponse)
def delete_listing(listing_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_owner)):
    listing = db.query(Listing).filter(Listing.id == listing_id, Listing.owner_id == current_user.id).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
    db.delete(listing)
    db.commit()
    return MessageResponse(detail="Listing deleted")


@router.patch("/{listing_id}/fill", response_model=ListingResponse)
async def mark_listing_filled(
    listing_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_owner)
):
    listing = db.query(Listing).filter(Listing.id == listing_id, Listing.owner_id == current_user.id).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    listing.status = ListingStatus.filled
    db.commit()
    db.refresh(listing)

    await notification_service.notify_listing_filled(db, current_user, listing.title)
    return ListingResponse.from_orm_with_photos(listing)


@router.post("/{listing_id}/photos", response_model=ListingResponse)
def upload_listing_photos(
    listing_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_owner),
):
    listing = db.query(Listing).filter(Listing.id == listing_id, Listing.owner_id == current_user.id).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    ensure_dir(settings.UPLOAD_DIR)
    saved_paths = listing.photo_list()

    for file in files:
        ext = validate_image_file(file)
        filename = generate_unique_filename(ext)
        filepath = os.path.join(settings.UPLOAD_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(file.file.read())
        saved_paths.append(f"/uploads/room_images/{filename}")

    listing.photos = ",".join(saved_paths)
    db.commit()
    db.refresh(listing)
    return ListingResponse.from_orm_with_photos(listing)


# ---------- Tenant: browse / search listings ranked by compatibility ----------

@router.get("", response_model=PaginatedListingsResponse)
def browse_listings(
    location: Optional[str] = Query(None),
    min_budget: Optional[float] = Query(None),
    max_budget: Optional[float] = Query(None),
    room_type: Optional[RoomType] = Query(None),
    furnishing_status: Optional[FurnishingStatus] = Query(None),
    sort_by: str = Query("compatibility"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = listing_service.query_active_listings(
        db, location=location, min_budget=min_budget, max_budget=max_budget,
        room_type=room_type, furnishing_status=furnishing_status,
    )

    if sort_by == "rent_asc":
        query = query.order_by(Listing.rent.asc())
    elif sort_by == "rent_desc":
        query = query.order_by(Listing.rent.desc())
    elif sort_by == "newest":
        query = query.order_by(Listing.created_at.desc())

    all_listings = query.all()
    total = len(all_listings)

    results_with_scores: list[ListingWithScoreResponse] = []

    tenant_profile = None
    if current_user.role.value == "tenant":
        tenant_profile = db.query(TenantProfile).filter(TenantProfile.user_id == current_user.id).first()

    if sort_by == "compatibility" and tenant_profile:
        all_listings = listing_service.sort_listings_by_compatibility(db, current_user.id, all_listings)

    start = (page - 1) * page_size
    paged_listings = all_listings[start: start + page_size]

    for listing in paged_listings:
        base = ListingResponse.from_orm_with_photos(listing)
        score, explanation, source = None, None, None

        if tenant_profile:
            compat = compatibility_service.get_or_compute_compatibility(
                db, current_user.id, listing, tenant_profile
            )
            score, explanation, source = compat.score, compat.explanation, compat.source

        results_with_scores.append(
            ListingWithScoreResponse(
                **base.model_dump(),
                compatibility_score=score,
                compatibility_explanation=explanation,
                compatibility_source=source,
            )
        )

    return PaginatedListingsResponse(total=total, page=page, page_size=page_size, results=results_with_scores)

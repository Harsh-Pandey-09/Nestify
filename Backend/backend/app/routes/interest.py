from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import require_tenant, require_owner
from app.models.user import User
from app.models.listing import Listing
from app.models.tenant_profile import TenantProfile
from app.models.interest import Interest, InterestStatus
from app.schemas.interest import InterestCreateRequest, InterestStatusUpdateRequest, InterestResponse
from app.services import compatibility_service, notification_service

router = APIRouter(prefix="/api/interest", tags=["Interest"])


@router.post("", response_model=InterestResponse, status_code=201)
async def express_interest(
    payload: InterestCreateRequest, db: Session = Depends(get_db), current_user: User = Depends(require_tenant)
):
    listing = db.query(Listing).filter(Listing.id == payload.listing_id).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    existing = (
        db.query(Interest)
        .filter(Interest.tenant_id == current_user.id, Interest.listing_id == listing.id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You have already expressed interest in this listing")

    interest = Interest(tenant_id=current_user.id, listing_id=listing.id, status=InterestStatus.pending)
    db.add(interest)
    db.commit()
    db.refresh(interest)

    # Fetch/compute compatibility score to decide notification tier (high match vs regular)
    profile = db.query(TenantProfile).filter(TenantProfile.user_id == current_user.id).first()
    score = 0.0
    if profile:
        compat = compatibility_service.get_or_compute_compatibility(db, current_user.id, listing, profile)
        score = compat.score

    await notification_service.notify_owner_of_interest(db, listing.owner, current_user.name, listing.title, score)

    return interest


@router.get("/sent", response_model=List[InterestResponse])
def get_sent_interests(db: Session = Depends(get_db), current_user: User = Depends(require_tenant)):
    return (
        db.query(Interest)
        .filter(Interest.tenant_id == current_user.id)
        .order_by(Interest.created_at.desc())
        .all()
    )


@router.get("/received", response_model=List[InterestResponse])
def get_received_interests(db: Session = Depends(get_db), current_user: User = Depends(require_owner)):
    return (
        db.query(Interest)
        .join(Listing, Interest.listing_id == Listing.id)
        .filter(Listing.owner_id == current_user.id)
        .order_by(Interest.created_at.desc())
        .all()
    )


@router.patch("/{interest_id}/accept", response_model=InterestResponse)
async def accept_interest(interest_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_owner)):
    return await _update_interest_status(db, interest_id, current_user, InterestStatus.accepted)


@router.patch("/{interest_id}/decline", response_model=InterestResponse)
async def decline_interest(interest_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_owner)):
    return await _update_interest_status(db, interest_id, current_user, InterestStatus.declined)


async def _update_interest_status(db: Session, interest_id: int, owner: User, new_status: InterestStatus) -> Interest:
    interest = (
        db.query(Interest)
        .join(Listing, Interest.listing_id == Listing.id)
        .filter(Interest.id == interest_id, Listing.owner_id == owner.id)
        .first()
    )
    if not interest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interest not found")

    interest.status = new_status
    db.commit()
    db.refresh(interest)

    tenant = db.query(User).filter(User.id == interest.tenant_id).first()
    await notification_service.notify_tenant_of_decision(
        db, tenant, interest.listing.title, accepted=(new_status == InterestStatus.accepted)
    )

    return interest

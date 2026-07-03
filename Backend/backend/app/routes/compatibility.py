from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import require_tenant
from app.models.user import User
from app.models.listing import Listing
from app.models.tenant_profile import TenantProfile
from app.schemas.compatibility import CompatibilityResponse
from app.services import compatibility_service

router = APIRouter(prefix="/api/compatibility", tags=["Compatibility"])


@router.get("/{listing_id}", response_model=CompatibilityResponse)
def get_compatibility(listing_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_tenant)):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    profile = db.query(TenantProfile).filter(TenantProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Create your tenant profile first to compute compatibility",
        )

    return compatibility_service.get_or_compute_compatibility(db, current_user.id, listing, profile)


@router.post("/{listing_id}/recompute", response_model=CompatibilityResponse)
def recompute_compatibility(
    listing_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_tenant)
):
    """Force a fresh LLM/fallback computation, e.g. after the tenant updates their profile."""
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    profile = db.query(TenantProfile).filter(TenantProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tenant profile not found")

    return compatibility_service.get_or_compute_compatibility(
        db, current_user.id, listing, profile, force_recompute=True
    )

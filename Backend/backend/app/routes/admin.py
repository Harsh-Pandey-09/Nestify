from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import require_admin
from app.models.user import User, UserRole
from app.models.listing import Listing, ListingStatus
from app.models.interest import Interest, InterestStatus
from app.models.chat import ChatMessage
from app.models.compatibility import Compatibility
from app.schemas.user import UserResponse
from app.schemas.listing import ListingResponse
from app.schemas.common import AdminActivitySummary, MessageResponse

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/users", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return db.query(User).order_by(User.created_at.desc()).all()


@router.delete("/users/{user_id}", response_model=MessageResponse)
def deactivate_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.is_active = False
    db.commit()
    return MessageResponse(detail="User deactivated")


@router.get("/listings", response_model=List[ListingResponse])
def list_all_listings(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    listings = db.query(Listing).order_by(Listing.created_at.desc()).all()
    return [ListingResponse.from_orm_with_photos(l) for l in listings]


@router.delete("/listings/{listing_id}", response_model=MessageResponse)
def delete_any_listing(listing_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
    db.delete(listing)
    db.commit()
    return MessageResponse(detail="Listing deleted")


@router.get("/activity", response_model=AdminActivitySummary)
def platform_activity(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return AdminActivitySummary(
        total_users=db.query(User).count(),
        total_tenants=db.query(User).filter(User.role == UserRole.tenant).count(),
        total_owners=db.query(User).filter(User.role == UserRole.owner).count(),
        total_listings=db.query(Listing).count(),
        active_listings=db.query(Listing).filter(Listing.status == ListingStatus.active).count(),
        filled_listings=db.query(Listing).filter(Listing.status == ListingStatus.filled).count(),
        total_interests=db.query(Interest).count(),
        pending_interests=db.query(Interest).filter(Interest.status == InterestStatus.pending).count(),
        accepted_interests=db.query(Interest).filter(Interest.status == InterestStatus.accepted).count(),
        total_messages=db.query(ChatMessage).count(),
        total_compatibility_scores=db.query(Compatibility).count(),
        llm_scores=db.query(Compatibility).filter(Compatibility.source == "llm").count(),
        fallback_scores=db.query(Compatibility).filter(Compatibility.source == "fallback").count(),
    )

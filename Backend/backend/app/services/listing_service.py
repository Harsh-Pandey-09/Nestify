from typing import Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.listing import Listing, ListingStatus, RoomType, FurnishingStatus
from app.models.compatibility import Compatibility


def query_active_listings(
    db: Session,
    location: Optional[str] = None,
    min_budget: Optional[float] = None,
    max_budget: Optional[float] = None,
    room_type: Optional[RoomType] = None,
    furnishing_status: Optional[FurnishingStatus] = None,
):
    q = db.query(Listing).filter(Listing.status == ListingStatus.active)

    if location:
        q = q.filter(Listing.location.ilike(f"%{location}%"))
    if min_budget is not None:
        q = q.filter(Listing.rent >= min_budget)
    if max_budget is not None:
        q = q.filter(Listing.rent <= max_budget)
    if room_type:
        q = q.filter(Listing.room_type == room_type)
    if furnishing_status:
        q = q.filter(Listing.furnishing_status == furnishing_status)

    return q


def sort_listings_by_compatibility(db: Session, tenant_id: int, listings: list[Listing]) -> list[Listing]:
    scores = {
        c.listing_id: c.score
        for c in db.query(Compatibility).filter(
            Compatibility.tenant_id == tenant_id,
            Compatibility.listing_id.in_([l.id for l in listings]),
        )
    }
    return sorted(listings, key=lambda l: scores.get(l.id, -1), reverse=True)

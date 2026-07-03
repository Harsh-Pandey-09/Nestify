import logging

from sqlalchemy.orm import Session

from app.models.compatibility import Compatibility
from app.models.listing import Listing
from app.models.tenant_profile import TenantProfile
from app.services import llm_service, fallback_service

logger = logging.getLogger(__name__)


def _listing_to_dict(listing: Listing) -> dict:
    return {
        "title": listing.title,
        "location": listing.location,
        "rent": listing.rent,
        "available_from": str(listing.available_from),
        "room_type": listing.room_type.value if hasattr(listing.room_type, "value") else listing.room_type,
        "furnishing_status": listing.furnishing_status.value
        if hasattr(listing.furnishing_status, "value")
        else listing.furnishing_status,
    }


def _tenant_to_dict(profile: TenantProfile) -> dict:
    return {
        "preferred_location": profile.preferred_location,
        "budget_min": profile.budget_min,
        "budget_max": profile.budget_max,
        "move_in_date": str(profile.move_in_date) if profile.move_in_date else None,
    }


def get_or_compute_compatibility(
    db: Session, tenant_id: int, listing: Listing, tenant_profile: TenantProfile, force_recompute: bool = False
) -> Compatibility:
    """
    Returns the cached Compatibility row for (tenant, listing) if present,
    otherwise computes it (LLM first, rule-based fallback on any failure),
    stores it, and returns it. Never recomputes on every request unless
    force_recompute=True (e.g. tenant/listing data changed).
    """
    existing = (
        db.query(Compatibility)
        .filter(Compatibility.tenant_id == tenant_id, Compatibility.listing_id == listing.id)
        .first()
    )
    if existing and not force_recompute:
        return existing

    listing_dict = _listing_to_dict(listing)
    tenant_dict = _tenant_to_dict(tenant_profile)

    source = "llm"
    try:
        result = llm_service.get_llm_compatibility_score(listing_dict, tenant_dict)
        score, explanation = result.score, result.explanation
    except Exception as exc:  # noqa: BLE001 - any LLM failure triggers fallback
        logger.warning("LLM compatibility scoring failed, using fallback: %s", exc)
        source = "fallback"
        score, explanation = fallback_service.compute_fallback_score(listing_dict, tenant_dict)

    if existing:
        existing.score = score
        existing.explanation = explanation
        existing.source = source
        db.commit()
        db.refresh(existing)
        return existing

    record = Compatibility(
        tenant_id=tenant_id,
        listing_id=listing.id,
        score=score,
        explanation=explanation,
        source=source,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

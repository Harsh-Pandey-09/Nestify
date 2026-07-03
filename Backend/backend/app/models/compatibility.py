from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, Float, ForeignKey, Text, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class Compatibility(Base):
    """
    Stores the AI (or fallback) compatibility score for a given
    tenant-listing pair. Computed once and cached; not recomputed
    on every request unless profile/listing data changes.
    """
    __tablename__ = "compatibility_scores"
    __table_args__ = (UniqueConstraint("tenant_id", "listing_id", name="uq_tenant_listing"),)

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    listing_id = Column(Integer, ForeignKey("listings.id", ondelete="CASCADE"), nullable=False)

    score = Column(Float, nullable=False)  # 0-100
    explanation = Column(Text, nullable=False)
    source = Column(String(20), nullable=False, default="llm")  # "llm" or "fallback"

    computed_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    listing = relationship("Listing", back_populates="compatibility_scores")

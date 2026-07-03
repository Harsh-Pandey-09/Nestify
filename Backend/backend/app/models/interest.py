import enum
from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class InterestStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"


class Interest(Base):
    __tablename__ = "interests"
    __table_args__ = (UniqueConstraint("tenant_id", "listing_id", name="uq_interest_tenant_listing"),)

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    listing_id = Column(Integer, ForeignKey("listings.id", ondelete="CASCADE"), nullable=False)

    status = Column(Enum(InterestStatus), nullable=False, default=InterestStatus.pending)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    listing = relationship("Listing", back_populates="interests")
    chat_messages = relationship("ChatMessage", back_populates="interest", cascade="all, delete-orphan")

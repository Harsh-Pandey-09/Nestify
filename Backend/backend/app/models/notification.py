import enum
from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, Enum, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base


class NotificationType(str, enum.Enum):
    high_match_interest = "high_match_interest"
    interest_received = "interest_received"
    interest_accepted = "interest_accepted"
    interest_declined = "interest_declined"
    new_message = "new_message"
    listing_filled = "listing_filled"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    type = Column(Enum(NotificationType), nullable=False)
    message = Column(String(500), nullable=False)
    is_read = Column(Boolean, default=False)
    email_sent = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")

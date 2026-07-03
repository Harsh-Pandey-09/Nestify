import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Date, Float, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class RoomType(str, enum.Enum):
    private_room = "private_room"
    shared_room = "shared_room"
    entire_place = "entire_place"


class FurnishingStatus(str, enum.Enum):
    furnished = "furnished"
    semi_furnished = "semi_furnished"
    unfurnished = "unfurnished"


class ListingStatus(str, enum.Enum):
    active = "active"
    filled = "filled"


class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    title = Column(String(190), nullable=False)
    location = Column(String(190), nullable=False, index=True)
    rent = Column(Float, nullable=False)
    available_from = Column(Date, nullable=False)
    room_type = Column(Enum(RoomType), nullable=False)
    furnishing_status = Column(Enum(FurnishingStatus), nullable=False)
    description = Column(Text, nullable=True)
    # comma-separated list of photo URLs / stored file paths
    photos = Column(Text, nullable=True)
    status = Column(Enum(ListingStatus), nullable=False, default=ListingStatus.active)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="listings")
    compatibility_scores = relationship("Compatibility", back_populates="listing", cascade="all, delete-orphan")
    interests = relationship("Interest", back_populates="listing", cascade="all, delete-orphan")

    def photo_list(self):
        return self.photos.split(",") if self.photos else []

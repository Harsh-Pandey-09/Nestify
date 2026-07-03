from datetime import datetime, date
from typing import Optional, List, Any
from pydantic import BaseModel, Field, field_validator

from app.models.listing import RoomType, FurnishingStatus, ListingStatus


class ListingCreateRequest(BaseModel):
    title: str = Field(..., max_length=190)
    location: str = Field(..., max_length=190)
    rent: float = Field(..., gt=0)
    available_from: date
    room_type: RoomType
    furnishing_status: FurnishingStatus
    description: Optional[str] = None


class ListingUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, max_length=190)
    location: Optional[str] = Field(None, max_length=190)
    rent: Optional[float] = Field(None, gt=0)
    available_from: Optional[date] = None
    room_type: Optional[RoomType] = None
    furnishing_status: Optional[FurnishingStatus] = None
    description: Optional[str] = None


class OwnerBrief(BaseModel):
    id: int
    name: str
    email: str

    model_config = {"from_attributes": True}


class ListingResponse(BaseModel):
    id: int
    owner_id: int
    title: str
    location: str
    rent: float
    available_from: date
    room_type: RoomType
    furnishing_status: FurnishingStatus
    description: Optional[str]
    photos: List[str] = []
    status: ListingStatus
    created_at: datetime
    updated_at: datetime
    owner: Optional[OwnerBrief] = None

    model_config = {"from_attributes": True}

    @field_validator("photos", mode="before")
    @classmethod
    def coerce_photos(cls, value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [p for p in value.split(",") if p]
        return value

    @classmethod
    def from_orm_with_photos(cls, listing):
        return cls.model_validate(listing)


class ListingWithScoreResponse(ListingResponse):
    """Used in tenant browse/search results — includes cached compatibility score."""
    compatibility_score: Optional[float] = None
    compatibility_explanation: Optional[str] = None
    compatibility_source: Optional[str] = None  # "llm" | "fallback"


class ListingFilterParams(BaseModel):
    location: Optional[str] = None
    min_budget: Optional[float] = None
    max_budget: Optional[float] = None
    room_type: Optional[RoomType] = None
    furnishing_status: Optional[FurnishingStatus] = None
    sort_by: Optional[str] = Field("compatibility", description="compatibility | rent_asc | rent_desc | newest")
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=50)


class PaginatedListingsResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: List[ListingWithScoreResponse]

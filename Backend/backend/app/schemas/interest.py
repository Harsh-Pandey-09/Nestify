from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.models.interest import InterestStatus
from app.schemas.listing import ListingResponse
from app.schemas.user import UserResponse


class InterestCreateRequest(BaseModel):
    listing_id: int


class InterestStatusUpdateRequest(BaseModel):
    status: InterestStatus  # accepted | declined


class InterestResponse(BaseModel):
    id: int
    tenant_id: int
    listing_id: int
    status: InterestStatus
    created_at: datetime
    updated_at: datetime
    listing: Optional[ListingResponse] = None
    tenant: Optional[UserResponse] = None

    model_config = {"from_attributes": True}

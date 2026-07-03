from datetime import datetime
from pydantic import BaseModel

from app.models.notification import NotificationType


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    type: NotificationType
    message: str
    is_read: bool
    email_sent: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationMarkReadRequest(BaseModel):
    is_read: bool = True

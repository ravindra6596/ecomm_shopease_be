from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: int
    title: str
    body: str
    is_read: bool
    notification_type: str
    reference_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class SendNotificationToAllSchema(BaseModel):
    title: str
    body: str
    notification_type: str

class SendNotificationToUsersSchema(BaseModel):
    user_ids: List[int]
    title: str
    body: str
    notification_type: str
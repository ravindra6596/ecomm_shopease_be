from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class BannerCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category_id: Optional[int] = None


class BannerUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    is_active: Optional[bool] = None

class BannerResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    image_url: str
    category_image_url: Optional[str] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }
from datetime import datetime

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List

from app.utils.strings import ConstStrings


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    discount: Optional[float] = Field(None, ge=0, le=100)
    return_policy: Optional[str] = None
    category_id: int
    @field_validator("name")
    @classmethod
    def name_must_be_alpha(cls, v):
        if v.strip().isdigit():
            raise ValueError(ConstStrings.PRODUCT_NAME_EMPTY)
        return v

class ProductUpdate(BaseModel):
    name: Optional[str]= None
    description: Optional[str]= None
    price: Optional[float]= None
    discount: Optional[float] = Field(None, ge=0, le=100)
    return_policy: Optional[str] = None
    category_id: Optional[int]= None
    @field_validator("name")
    @classmethod
    def name_must_be_alpha(cls, v):
        if v is not None and v.strip().isdigit():
            raise ValueError(ConstStrings.PRODUCT_NAME_STRINGS)
        return v


class ProductImageResponse(BaseModel):
    id: int
    image_url: str

    model_config = {
        "from_attributes": True
    }

class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    discount: Optional[float] = None
    discount_price: Optional[float] = None
    return_policy: Optional[str] = None
    category_id: int
    category_name: Optional[str] = None
    images: List[ProductImageResponse] = []
    is_deleted: bool
    is_featured: bool
    created_by: Optional[int] = None
    deleted_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = {
        "from_attributes": True
    }



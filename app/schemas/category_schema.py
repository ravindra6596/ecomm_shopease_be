from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator

from app.schemas.product_schema import ProductResponse
from app.utils.strings import ConstStrings


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1)

    @field_validator("name")
    @classmethod
    def name_must_be_alpha(cls, v):
        v = v.strip()

        if not v:
            raise ValueError(ConstStrings.CATEGORY_NAME_EMPTY)

        if v.isdigit():
            raise ValueError(ConstStrings.CATEGORY_NAME_STRINGS)

        return v

# Update category
class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if v is None:
            return v

        v = v.strip()

        if not v:
            raise ValueError(ConstStrings.CATEGORY_NAME_EMPTY)

        if v.isdigit():
            raise ValueError(ConstStrings.CATEGORY_NAME_STRINGS)

        return v

class CategoryImageResponse(BaseModel):
    id: int
    image_url: str
    model_config = {
        "from_attributes": True
    }

class CategoryResponse(BaseModel):
    id: int
    name: str
    images: List[CategoryImageResponse] = []
    products_count: int = 0
    is_deleted: bool
    deleted_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    model_config = {
        "from_attributes": True
    }

class CategoryByIdResponse(BaseModel):
    id: int
    name: str
    images: List[CategoryImageResponse] = []
    products_count: int = 0
    products: List[ProductResponse] = []
    is_deleted: bool
    deleted_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = {
        "from_attributes": True
    }
class TopCategoryResponse(BaseModel):
    category_id: int
    category_name: str
    total_quantity: int
    total_sales: float
    sales_percentage: float
    images: List[CategoryImageResponse] = []
    model_config = {
        "from_attributes": True
    }
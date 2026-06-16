from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field

class AddToCartSchema(BaseModel):
    product_id: int
    # quantity: int = Field(..., gt=0)

class CartResponse(BaseModel):
    id: int
    cart_id: int
    product_id: int
    quantity: int

    product_name: str
    product_price: float
    total_price: float
    discount_price: float
    discount: float
    total_discount_price: Optional[float] = None

    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }

class UpdateCartQuantitySchema(BaseModel):
    quantity: int = Field(..., gt=0)

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_price: float
    quantity: int
    total_price: float

    model_config = {
        "from_attributes": True
    }


class GetCartResponse(BaseModel):
    id: int
    user_id: int
    total_items: int
    grand_total: float
    items: List[CartItemResponse]

    model_config = {
        "from_attributes": True
    }

class AdminCartResponse(BaseModel):
    id: int

    user_id: int
    user_name: Optional[str] = None
    user_email: Optional[str] = None

    total_items: int
    grand_total: float

    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }
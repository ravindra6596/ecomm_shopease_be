from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

from app.schemas.address_schema import AddressResponse
from app.schemas.order_schema import OrderItemResponse, OrderResponse


class UserCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=3,
        max_length=50
    )
    email: EmailStr
    password: str = Field(
        ...,
        min_length=6,
        max_length=20
    )



class UserLogin(BaseModel):
    email: EmailStr
    password: str
    guest_id: str = None
    fcm_token: str = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_active: bool
    role: str
    created_at: datetime
    updated_at: datetime


    model_config = {
        "from_attributes": True
    }

class UserDetailsResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_active: bool
    role: str

    addresses: List[AddressResponse] = []

    orders: List[OrderResponse] = []

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from app.schemas.address_schema import AddressResponse
from app.utils.enums import OrderStatus, PaymentStatus, PaymentMethod


class CreateOrderSchema(BaseModel):
    address_id: int
    payment_method: PaymentMethod

class UpdateOrderSchema(BaseModel):

    status: Optional[str] = None
    payment_status: Optional[str] = None

class OrderItemResponse(BaseModel):

    product_id: int
    product_name: str
    image_url: Optional[str] = None
    quantity: int
    price: float
    total_price: float
    discount_price: float
    discount: float
    total_discount_price: Optional[float] = None

    model_config = {
        "from_attributes": True
    }

class OrderResponse(BaseModel):
    id: int
    user_name: str
    user_id: int
    address_id: int
    total_amount: float
    total_discount_price: Optional[float] = None
    shipping: Optional[float] = None
    status: str
    payment_status: str
    payment_method: str
    created_at: datetime
    updated_at: datetime
    delivery_date: Optional[datetime] = None
    items: List[OrderItemResponse]
    address: AddressResponse

    model_config = {
        "from_attributes": True
    }

class UpdateOrderAddressSchema(BaseModel):
    address_id: int

class UpdateOrderStatusSchema(BaseModel):
    status: OrderStatus

class UpdatePaymentStatusSchema(BaseModel):
    payment_status: PaymentStatus

class OrderCreateResponse(BaseModel):
    order_id: int
    payment_method: str
    order_date: datetime
    delivery_date: datetime
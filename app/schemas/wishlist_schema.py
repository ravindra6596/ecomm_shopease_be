from datetime import datetime

from pydantic import BaseModel


class AddWishlistSchema(BaseModel):
    product_id: int

class WishlistResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_price: float
    discount_price: float
    discount: float
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
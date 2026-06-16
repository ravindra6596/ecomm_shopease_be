from datetime import datetime

from pydantic import BaseModel
from typing import List, Optional

from app.schemas.address_schema import AddressResponse
from app.schemas.category_schema import TopCategoryResponse
from app.schemas.product_schema import ProductImageResponse


class HomeProductResponse(BaseModel):
    id: int
    name: str
    price: float
    discount_price: float
    discount: float
    images: List[ProductImageResponse] = []


class HomeBannerResponse(BaseModel):
    banner_id: int
    title: str
    description: str
    image_url: str
    category_image_url: Optional[str] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None



class TopCategoryProductResponse(BaseModel):
    category_id: int
    category_name: str
    products: List[HomeProductResponse]


class HomeResponse(BaseModel):
    delivery_address: Optional[AddressResponse] = None
    banners: List[HomeBannerResponse]
    trending_products: List[HomeProductResponse]
    featured_products: List[HomeProductResponse]
    popular_products: List[HomeProductResponse]
    new_arrivals: List[HomeProductResponse]
    # top_category_products: List[TopCategoryProductResponse]
from enum import Enum

from app.utils.strings import ConstStrings


class ProductSortField(str, Enum):
    id = "id"
    name = "name"
    price = "price"
    created_at = "created_at"

class CategorySortField(str, Enum):
    id = "id"
    name = "name"
    created_at = "created_at"

class SortOrder(str, Enum):
    asc = ConstStrings.ASCENDING
    desc = ConstStrings.DESCENDING

class SearchField(str, Enum):
    id = "id"
    name = "name"
    email = "email"
    role = "role"

class SortField(str, Enum):
    id = "id"
    name = "name"
    email = "email"
    role = "role"
    created_at = "created_at"

class OrderStatus(str, Enum):
    pending = "pending"
    placed = "placed"
    shipped = "shipped"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"
    cancelled = "cancelled"

class PaymentStatus(str, Enum):
    pending = "pending"
    success = "success"
    failed = "failed"

class PaymentMethod(str, Enum):
    cod = "cod"
    online = "online"

class OrderSortField(str, Enum):
    id = "id"
    total_amount = "total_amount"
    user_name = "user_name"
    status = "status"
    payment_status = "payment_status"
    payment_method = "payment_method"
    created_at = "created_at"
    updated_at = "updated_at"


class CartSortField(str, Enum):
    id = "id"
    user_name = "user_name"
    user_email = "user_email"
    quantity = "total_items"
    total_amount = "grand_total"
    created_at = "created_at"

class NotificationType(str, Enum):
    ORDER_PLACED = "order_placed"
    ORDER_SHIPPED = "order_shipped"
    ORDER_OUT_FOR_DELIVERY='out_for_delivery'
    ORDER_DELIVERED = "order_delivered"
    ORDER_CANCELLED = "order_cancelled"
    ORDER_RETURNED = "order_returned"
    OFFER = "offer"
    ORDER = "order"
    PRODUCT = "product"
    WISHLIST = "wishlist"
    PRICE_DROP = "price_drop"
    PAYMENT_SUCCESS = "payment_success"
    PAYMENT_FAILED = "payment_failed"

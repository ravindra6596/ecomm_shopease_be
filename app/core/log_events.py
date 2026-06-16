from enum import Enum

class UserEvent(str, Enum):
    CREATED = "user.created"
    UPDATED = "user.updated"
    DELETED = "user.deleted"
    FETCHED = "user.fetched"
    LISTED = "user.listed"
    LOGIN = "user.login"
    LOGOUT = "user.logout"
    REGISTERED = "user.registered"
    PASSWORD_CHANGED = "user.password_changed"
    PROFILE_UPDATED = "user.profile_updated"


class CategoryEvent(str, Enum):
    CREATED = "category.created"
    UPDATED = "category.updated"
    DELETED = "category.deleted"
    FETCHED = "category.fetched"
    LISTED = "category.listed"
    BULK_CREATED = "category.bulk_created"


class ProductEvent(str, Enum):
    CREATED = "product.created"
    UPDATED = "product.updated"
    DELETED = "product.deleted"
    FETCHED = "product.fetched"
    LISTED = "product.listed"
    OUT_OF_STOCK = "product.out_of_stock"
    IN_STOCK = "product.in_stock"
    PRICE_UPDATED = "product.price_updated"

class CartEvent(str, Enum):
    CREATED = "cart.created"
    UPDATED = "cart.updated"
    DELETED = "cart.deleted"
    FETCHED = "cart.fetched"
    LISTED = "cart.listed"
    OUT_OF_STOCK = "product.out_of_stock"
    IN_STOCK = "product.in_stock"
    PRICE_UPDATED = "product.price_updated"


class OrderEvent(str, Enum):
    CREATED = "order.created"
    UPDATED = "order.updated"
    DELETED = "order.deleted"
    FETCHED = "order.fetched"
    LISTED = "order.listed"


class AddressEvent(str, Enum):
    CREATED = "address.created"
    UPDATED = "address.updated"
    DELETED = "address.deleted"
    FETCHED = "address.fetched"
    LISTED = "address.listed"



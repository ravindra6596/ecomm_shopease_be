class ConstStrings:
# Authentication messages
    INTERNAL_SERVER_ERROR = 'Internal Server Error'
    VALIDATION_ERROR = 'Validation Error'
    USER_REGISTER = 'Account created successfully. Please check your email and verify your account.'
    RATE_EXCEEDED = 'Rate exceeded'
    TOO_MANY = 'Too many failed attempts. Try later!'
    LOGIN_SUCCESS = 'Login successful'
    LOGOUT_SUCCESS = 'Logged out successfully'
    USER_EXISTS = 'User already exists'
    NO_USER = 'No registered user!'
    INVALID_PASSWORD = 'Invalid password'
    ACCOUNT_INACTIVE = 'Account is inactive'
    NEW_ACCESS_TOKEN = 'New access token generated'
    TOKEN_REQUIRED = 'Unauthorized. Token is required'
    TOKEN_EXPIRED = 'Token is expired / blacklisted'
    INVALID_TOKEN = 'Invalid or expired token'
    INVALID_REFRESH_TOKEN = 'Invalid refresh token'
    REFRESH_TOKEN_EXPIRED = "Refresh token expired"
    HEALTH_CHECK_API = "Health Check API"
    NOT_ALLOWED = "Not allowed"

# Routes
    HEALTH_CHECK_ROUTE = 'health-check'
    GET_POST_ROUTE = ''
    ADMIN_ROUTE = '/admin'
    ID_ROUTE = '/{id}'
    AUTH_PREFIX = '/auth'
    AUTH_TAG = 'Authentication'
    REGISTER_ROUTE = '/register'
    LOGIN_ROUTE = '/login'
    REFRESH_TOKEN_ROUTE = '/refresh'
    LOGOUT_ROUTE = '/logout'

    CATEGORY_PREFIX = '/categories'
    CATEGORY_TAG = 'Categories'
    BULK_CATEGORY_ROUTE = '/bulk'
    TOP_CATEGORY_ROUTE = '/top'

    PRODUCT_PREFIX = '/products'
    PRODUCT_TAG = 'Products'
    BULK_PRODUCT_ROUTE = '/bulk'

    USERS_PREFIX = '/users'
    USERS_TAG = 'Users'
    USERS_ME = '/me'
    USERS_PROFILE = '/profile'
    USERS_EMAIL = '/email/{email}'

    CART_PREFIX = '/cart'
    CART_TAG = 'Cart'
    CART_CLEAR = '/clear'

    WISHLIST_PREFIX = '/wishlist'
    WISHLIST_TAG = 'Wishlist'

    ORDER_PREFIX = '/orders'
    ORDER_TAG = 'Orders'
    ORDER_ADDRESS = '/{id}/address'
    ORDER_CANCEL = '/{id}/cancel'
    ORDER_STATUS = '/{id}/status'
    ORDER_PAYMENT = '/{id}/payment'
    ORDER_INVOICE = '/{id}/invoice'

    ADDRESS_PREFIX = '/address'
    ADDRESS_TAG = 'Addresses'

    NOTIFICATION_PREFIX = '/notifications'
    NOTIFICATION_TAG = 'Notifications'
    SEND_NOTIFICATION_TO_SELECTED_USERS = '/selected-users'

    HOME_PREFIX = '/home'
    HOME_TAG = 'Home'

    BANNER_PREFIX = '/banners'
    BANNER_TAG = 'Banners'

# Database Table
    CATEGORIES_TABLE = 'categories'
    CATEGORIES_IMAGES_TABLE = 'categories_images'
    PRODUCTS_TABLE = 'products'
    PRODUCTS_IMAGES_TABLE = 'products_images'
    USER_TABLE = 'user'
    BLACKLIST_TOKEN_TABLE = 'blacklisted_tokens'
    CART_TABLE = 'cart'
    CART_ITEMS_TABLE = 'cart_items'
    WISHLIST_ITEMS_TABLE = 'wishlist'
    ORDERS_TABLE = 'orders'
    ORDER_ITEMS_TABLE = 'order_items'
    ADDRESS_TABLE = 'addresses'
    NOTIFICATIONS_TABLE = 'notifications'

# Normal Strings
    USER_ID_FIELD = 'user_id'
    TRUE= 'true'
    FALSE = 'false'
    ASCENDING = 'asc'
    DESCENDING = 'desc'
    NO_UPDATE = 'No fields provided for update'
    NO_CHANGE = 'No changes detected'

# Categories message
    CATEGORY_CREATED = 'Category created successfully'
    CATEGORY_FETCHED = 'Categories fetched successfully'
    MULTI_CATEGORY_CREATED = 'Categories created successfully'
    CATEGORY_UPDATED = 'Categories updated successfully'
    CATEGORY_DELETED = 'Categories deleted successfully'
    CATEGORY_NAME_EMPTY = 'Category name cannot be empty'
    CATEGORY_NAME_STRINGS = 'Category name cannot be numeric'
    CATEGORY_EXISTS = 'Category name already exists'
    NO_CATEGORY = 'Category not found'
    INVALID_CATEGORY = 'Invalid category id'

# Products message
    PRODUCT_CREATED = 'Product created successfully'
    PRODUCTS_FETCHED = 'Products fetched successfully'
    MULTI_PRODUCTS_CREATED = 'Products created successfully'
    PRODUCT_UPDATED = 'Product updated successfully'
    PRODUCT_DELETED = 'Product deleted successfully'
    NO_PRODUCT = 'Product not found'
    PRODUCT_NAME_EMPTY = 'Product name cannot be empty'
    PRODUCT_NAME_STRINGS = 'Product name cannot be numeric'
    PRICE_NOT_ZERO = 'Price must be greater than 0'
    PRODUCT_EXISTS = 'Product name already exists'
    IMAGE_NOT_FOUND = "Image not found"
    IMAGE_DELETED = "Image deleted successfully"

# Users message
    USER_FETCHED = 'User fetched successfully'
    USER_NOT_FOUND = 'User not found'
    USER_OWN_PROFILE = 'You can only update your own profile'
    USER_UPDATED = 'Profile updated successfully'
    USER_DELETED = 'Profile deleted successfully'

# CART message
    CART_CREATED = 'Item added to cart.'
    ALREADY_IN_CART = 'Item already added'
    CART_FETCHED = 'Cart items fetched successfully'
    CART_NOT_FOUND = 'No Cart found'
    CART_UPDATED = 'Cart quantity updated'
    CART_DELETED = 'Cart cleared successfully'
    CART_ITEM_REMOVED = "Cart item removed successfully"

# Wishlist messages
    WISHLIST_ADDED = "Wishlist added successfully"
    WISHLIST_FETCHED = "Wishlist fetched successfully"
    WISHLIST_REMOVED = "Wishlist removed successfully"
    ALREADY_IN_WISHLIST = "Product already in wishlist"
    WISHLIST_NOT_FOUND = "Wishlist item not found"
    WISHLIST_CLEARED = "Wishlist cleared successfully"

    # Orders
    ORDER_CREATED = "Order placed successfully"
    CART_EMPTY = "Cart is empty"
    ORDER_FETCHED = "Orders fetched successfully"
    ORDER_NOT_FOUND = "Order not found"
    ORDER_UPDATED = "Order updated successfully"
    ORDER_DELETED = "Order deleted successfully"
    OWN_ORDER = 'You can only update your own order'
    ORDER_ADDRESS_UPDATED = "Order address updated successfully"
    ORDER_CANCELLED = "Order cancelled successfully"
    ORDER_STATUS_UPDATED = "Order status updated successfully"
    PAYMENT_STATUS_UPDATED = "Payment status updated successfully"
    ORDER_CANCEL_NOT_ALLOWED = "Order cannot be cancelled"
    ORDER_ADDRESS_UPDATE_NOT_ALLOWED = "Order address cannot be updated"

    # Address
    ADDRESS_CREATED = 'Address created successfully'
    ADDRESS_FETCHED = 'Address fetched successfully'
    ADDRESS_NOT_FOUND = 'Address not found'
    ADDRESS_UPDATED = 'Address updated successfully'
    ADDRESS_DELETED = 'Address deleted successfully'
    OWN_ADDRESS = 'You can only update your own address'

    # Notifications
    NOTIFICATION_FETCHED = 'Notifications fetched successfully'
    NOTIFICATION_NOT_FOUND = 'Notification not found'
    NOTIFICATION_UPDATED = 'Notification updated successfully'
    NOTIFICATION_DELETED = 'Notification deleted successfully'
    NOTIFICATION_READ = 'Notification read successfully'
    NOTIFICATION_SENT = 'Notification sent successfully'

    # Home
    HOME_DATA_FETCHED = 'Home data fetched successfully'
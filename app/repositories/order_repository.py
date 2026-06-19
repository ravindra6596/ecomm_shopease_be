# Create Order Repo
import math

from fastapi import HTTPException
from sqlalchemy import asc, func, String, cast, or_, desc
from sqlalchemy.orm import Session

from app.models import Product
from app.models.address_model import Address
from app.models.cart_item_model import CartItem
from app.models.cart_model import Cart
from app.models.order_items_model import OrderItem
from app.models.order_model import Order
from app.models.user_model import User
from app.utils.enums import OrderStatus, PaymentMethod, PaymentStatus
from app.utils.strings import ConstStrings

# Create Order Repo
def create_order_repo(
    db: Session,
    payload,
    token
):

    user_id = token.get(
        ConstStrings.USER_ID_FIELD
    )

    # Validate address
    address = db.query(Address).filter(
        Address.id == payload.address_id,
        Address.user_id == user_id
    ).first()

    if not address:
        raise HTTPException(
            status_code=404,
            detail=ConstStrings.ADDRESS_NOT_FOUND
        )

    # Get cart
    cart = db.query(Cart).filter(
        Cart.user_id == user_id
    ).first()

    if not cart:
        raise HTTPException(
            status_code=404,
            detail=ConstStrings.CART_NOT_FOUND
        )

    # Get cart items
    cart_items = db.query(CartItem).filter(
        CartItem.cart_id == cart.id
    ).all()

    if not cart_items:
        raise HTTPException(
            status_code=404,
            detail=ConstStrings.CART_EMPTY
        )

    # Calculate total
    grand_total = sum(
        item.product.price * item.quantity
        for item in cart_items
    )
    total_discount_price = sum(
        item.product.discount_price * item.quantity
        for item in cart_items
    )
    shipping = round((grand_total - total_discount_price) * 0.10)
    # Payment status logic
    payment_status = PaymentStatus.pending.value

    # Online payment
    if payload.payment_method.value == PaymentMethod.online.value:
        payment_status = PaymentStatus.success.value

    # Create order
    order = Order(
        user_id=user_id,
        address_id=payload.address_id,
        total_amount=grand_total,
        total_discount_price=round(total_discount_price),
        shipping=shipping,
        status=OrderStatus.placed.value,
        payment_status=PaymentStatus.pending.value,
        payment_method=payload.payment_method.value
    )

    db.add(order)
    db.flush()
    # Create order items
    for item in cart_items:

        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.product.price
        )

        db.add(order_item)
    db.commit()
    db.refresh(order)
    # Clear cart after order creation
    db.query(CartItem).filter(
        CartItem.cart_id == cart.id
    ).delete(
        synchronize_session=False
    )

    db.commit()

    return order
# Get Orders Repo
def get_orders_repo(
        db: Session,
        token,
        page: int,
        limit: int,
        search: str,
        order_status: str,
        payment_status: str,
        payment_method: str,
        sort_by: str,
        order: str,
):
    user_id = token.get(
        ConstStrings.USER_ID_FIELD
    )

    role = token.get("role")

    query = db.query(Order)

    # User -> own orders only
    if role == "user":
        query = query.filter(
            Order.user_id == user_id
        )

    # Search
    if search:
        query = query.join(User).join(OrderItem).join(Product)
        query = query.filter(
            or_(
                User.name.ilike(f"%{search}%"),
                Product.name.ilike(f"%{search}%"),
                cast(Order.id, String).ilike(f"%{search}%"),
                cast(Order.status, String).ilike(f"%{search}%"),
                cast(Order.payment_status, String).ilike(f"%{search}%"),
                cast(Order.payment_method, String).ilike(f"%{search}%"),
                cast(Order.total_amount, String).ilike(f"%{search}%"),
                cast(Order.created_at, String).ilike(f"%{search}%"),
            )
        )
    # Order Status Filter
    if order_status:
        query = query.filter(
            Order.status == order_status
        )

    # Payment Status Filter
    if payment_status:
        query = query.filter(
            Order.payment_status == payment_status
        )
        # Payment method Filter
    if payment_method:
        query = query.filter(
            Order.payment_method == payment_method
        )
    # Join user table for user_name sorting
    if sort_by == "user_name":

        query = query.join(User)

        sort_column = User.name

    else:
    # Sorting
        sort_column = getattr(Order, sort_by, None)

    try:
        column_type = sort_column.property.columns[0].type

        if isinstance(column_type, String):
            sort_column = func.lower(sort_column)

    except Exception:
        pass

    if order == ConstStrings.ASCENDING:
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    # Pagination
    total = query.count()

    total_pages = math.ceil(total / limit)

    offset = (page - 1) * limit

    orders = query.offset(offset).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "is_previous": page > 1,
        "is_next": page < total_pages,
        "items": orders
    }

# Get Order By id Repo
def get_order_by_id_repo(
    db: Session,
    order_id: int,
    token
):

    user_id = token.get(
        ConstStrings.USER_ID_FIELD
    )

    role = token.get("role")

    query = db.query(Order).filter(
        Order.id == order_id
    )

    # user -> own order only
    if role == "user":
        query = query.filter(
            Order.user_id == user_id
        )

    order = query.first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail=ConstStrings.ORDER_NOT_FOUND
        )

    return order

# Update Order Address Repo
def update_order_address_repo(
    db: Session,
    order_id: int,
    payload,
    token
):

    user_id = token.get(
        ConstStrings.USER_ID_FIELD
    )

    # validate order
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail=ConstStrings.ORDER_NOT_FOUND
        )

    # cannot update after shipped
    if order.status in ["shipped", "delivered"]:
        raise HTTPException(
            status_code=400,
            detail=ConstStrings.ORDER_ADDRESS_UPDATE_NOT_ALLOWED
        )

    # validate address ownership
    address = db.query(Address).filter(
        Address.id == payload.address_id,
        Address.user_id == user_id
    ).first()

    if not address:
        raise HTTPException(
            status_code=404,
            detail=ConstStrings.ADDRESS_NOT_FOUND
        )

    order.address_id = payload.address_id

    db.commit()
    db.refresh(order)

    return order

# Cancel Order Repo
def cancel_order_repo(
    db: Session,
    order_id: int,
    token
):

    user_id = token.get(
        ConstStrings.USER_ID_FIELD
    )

    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail=ConstStrings.ORDER_NOT_FOUND
        )

    # cannot cancel shipped/delivered
    if order.status in ["shipped", "delivered"]:
        raise HTTPException(
            status_code=400,
            detail=ConstStrings.ORDER_CANCEL_NOT_ALLOWED
        )

    order.status = "cancelled"

    db.commit()
    db.refresh(order)

    return order

# Update Order Status Repo
def update_order_status_repo(
    db: Session,
    order_id: int,
    payload
):

    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail=ConstStrings.ORDER_NOT_FOUND
        )

    # Cancelled order restriction
    if order.status == OrderStatus.cancelled.value:
        raise HTTPException(
            status_code=400,
            detail="Cancelled order cannot be updated"
        )

    # Online payment validation
    if order.payment_method == PaymentMethod.online.value:

        if (
            payload.status.value in [
                OrderStatus.shipped.value,
                OrderStatus.delivered.value
            ]
            and
            order.payment_status != PaymentStatus.success.value
        ):
            raise HTTPException(
                status_code=400,
                detail="Payment must be successful before shipping or delivery"
            )

    # Update status
    order.status = payload.status.value

    # COD Delivered -> payment success
    if (
        order.payment_method == PaymentMethod.cod.value
        and
        payload.status.value == OrderStatus.delivered.value
    ):
        order.payment_status = PaymentStatus.success.value

    db.commit()

    db.refresh(order)

    return order

# Update Payment Status Repo
def update_payment_status_repo(
    db: Session,
    order_id: int,
    payload
):

    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail=ConstStrings.ORDER_NOT_FOUND
        )

    order.payment_status = payload.payment_status.value

    # success
    if payload.payment_status.value == "success":

        order.status = "placed"

        # clear cart items
        cart = db.query(Cart).filter(
            Cart.user_id == order.user_id
        ).first()

        if cart:

            db.query(CartItem).filter(
                CartItem.cart_id == cart.id
            ).delete(
                synchronize_session=False
            )

    # failed
    elif payload.payment_status.value == "failed":

        order.status = "cancelled"

    db.commit()
    db.refresh(order)

    return order

def calculate_shipping(amount):
       return round(amount *10/100)
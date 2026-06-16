# Create Order Service
from sqlalchemy.orm import Session

from app.email_template.custom_template import build_email
from app.repositories import order_repository
from app.repositories.order_repository import get_order_by_id_repo
from app.schemas.order_schema import OrderItemResponse, OrderResponse
from app.services import notification_service
from app.utils.enums import NotificationType, OrderStatus
from app.utils.url_helper import build_image_url


# Create Order Service
def create_order_service(
    db: Session,
    payload,
    token
):
    # 🔥 SEND EMAIL HERE (business logic)
    user_email = token.get("email")  # or fetch from DB
    user_name = token.get("name")  # or fetch from DB
    order = order_repository.create_order_repo(db, payload, token)
    if user_email:
        # email_body = build_order_email(order)
        # email_body = build_email(user_name, "order_placed", order)
        subject, body = build_email(user_name, "order_placed", order)
        # send_email(
        #     to_email=user_email,
        #     subject=subject,
        #     body=body
        # )
    #     SEND NOTIFICATION HERE (business logic)
    notification_service.send_notification_service(
        db=db,
        user=order.user,
        title="Order Confirmed 🛒",
        body=f"Hello {user_name},Your order #{order.id} has been placed successfully.",
        notification_type=NotificationType.ORDER.value,
        reference_id=order.id
    )
    return order

# Get Orders Service
def get_orders_service(
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

    result = order_repository.get_orders_repo(
        db,
        token,
        page,
        limit,
        search,
        order_status,
        payment_status,
        payment_method,
        sort_by,
        order,
    )

    result["items"] = [

        OrderResponse(
            id=order.id,
            user_name=order.user.name,
            user_id=order.user_id,
            address_id=order.address_id,
            total_amount=order.total_amount,
            total_discount_price=order.total_discount_price,
            shipping=order.shipping,
            status=order.status,
            payment_status=order.payment_status,
            payment_method=order.payment_method,
            created_at=order.created_at,
            updated_at=order.updated_at,
            delivery_date=order.delivery_date,
            items=[
                OrderItemResponse(
                    product_id=item.product_id,
                    product_name=item.product.name,
                    image_url = build_image_url(item.product.images[0].image_url) if item.product.images else None,
                    quantity=item.quantity,
                    price=item.price,
                    total_price=item.quantity * item.price,
                    discount_price=item.product.discount_price * item.quantity,
                    discount=item.product.discount,
                    # total_discount_price=item.product.total_discount_price * item.quantity
                )
                for item in order.items
            ],

            address=order.address

        ).model_dump()

        for order in result["items"]
    ]

    return result
# Get Order By id Service
def get_order_by_id_service(
    db: Session,
    order_id: int,
    token
):

    return order_repository.get_order_by_id_repo(
        db,
        order_id,
        token
    )

# Update Order Address Service
def update_order_address_service(
    db: Session,
    order_id: int,
    payload,
    token
):

    return order_repository.update_order_address_repo(
        db,
        order_id,
        payload,
        token
    )

# Cancel Order Service
def cancel_order_service(
    db: Session,
    order_id: int,
    token
):
    order = order_repository.cancel_order_repo(
        db,
        order_id,
        token
    )
    user_email = token.get("email")
    user_name = token.get("name")
    subject, body = build_email(user_name, "cancelled", order)
    # send_email(
    #     to_email=user_email,
    #     subject=subject,
    #     body=body
    # )
    # Send Notification
    notification_service.send_notification_service(
        db=db,
        user=order.user,
        title="Order Cancelled ❌",
        body=f"Hello {user_name}, Your order #{order.id} has been cancelled successfully.",
        notification_type=NotificationType.ORDER.value,
        reference_id=order.id
    )
    return order

# Update Order Status Service
def update_order_status_service(
    db: Session,
    order_id: int,
    payload
):
    order_status_update = order_repository.update_order_status_repo(
        db,
        order_id,
        payload
    )
    user_email = order_status_update.user.email
    user_name = order_status_update.user.name
    status_map = {
        "placed": "order_placed",
        "shipped": "shipped",
        "out_for_delivery": "out_for_delivery",
        "delivered": "delivered",
        "cancelled": "cancelled"
    }
    email_type = status_map.get(order_status_update.status)
    subject, body = build_email(user_name, email_type, order_status_update)
    # send_email(
    #     to_email=user_email,
    #     subject=subject,
    #     body=body
    # )
    # Send Notification
    notification_map = {
        OrderStatus.placed.value: {
            "title": "Order Confirmed 🛒",
            "body": f"Hello {user_name}, your order #{order_status_update.id} has been placed successfully.",
            "type": NotificationType.ORDER_PLACED.value
        },
        OrderStatus.shipped.value: {
            "title": "Order Shipped 🚚",
            "body": f"Hello {user_name}, your order #{order_status_update.id} is on the way.",
            "type": NotificationType.ORDER_SHIPPED.value
        },
        OrderStatus.out_for_delivery.value: {
            "title": "Out for Delivery 📦",
            "body": f"Hello {user_name}, your order #{order_status_update.id} is out for delivery.",
            "type": NotificationType.ORDER_OUT_FOR_DELIVERY.value
        },
        OrderStatus.delivered.value: {
            "title": "Order Delivered ✅",
            "body": f"Hello {user_name}, your order #{order_status_update.id} has been delivered.",
            "type": NotificationType.ORDER_DELIVERED.value
        },
        OrderStatus.cancelled.value: {
            "title": "Order Cancelled ❌",
            "body": f"Hello {user_name}, your order #{order_status_update.id} has been cancelled.",
            "type": NotificationType.ORDER_CANCELLED.value
        }
    }
    notification_data = notification_map.get(order_status_update.status)
    notification_service.send_notification_service(
        db=db,
        user=order_status_update.user,
        title=notification_data["title"],
        body=notification_data["body"],
        notification_type=NotificationType.ORDER.value,
        reference_id=order_status_update.id
    )
    return order_status_update

# Update Payment Status Service
def update_payment_status_service(
    db: Session,
    order_id: int,
    payload
):

    return order_repository.update_payment_status_repo(
        db,
        order_id,
        payload
    )

from app.utils.pdf_generator import generate_order_invoice

# Order invoice
def download_invoice_service(
    db,
    order_id,
    token
):

    order = get_order_by_id_repo(
        db,
        order_id,
        token
    )

    pdf = generate_order_invoice(order)

    return pdf
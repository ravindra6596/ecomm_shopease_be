from app.models.order_model import Order
from app.repositories import chatbot_order_repository


def get_latest_order_statuses(
    db,
    token
):
    user_id = token["user_id"]

    order = (
        chatbot_order_repository
        .get_latest_order_repo(
            db,
            user_id
        )
    )

    if not order:
        return "You don't have any orders."

    return (
        f"Your latest order "
        f"#{order.id} "
        f"is currently "
        f"{order.status}."
    )


def get_user_orders(
    db,
    token
):
    user_id = token["user_id"]

    orders = (
        db.query(Order)
        .filter(Order.user_id == user_id)
        .order_by(Order.id.desc())
        .limit(5)
        .all()
    )

    if not orders:
        return "You don't have any orders."

    response = "Your recent orders:\n\n"

    for order in orders:
        response += (
            f"Order #{order.id} - "
            f"{order.status}\n"
        )

    return response


def get_latest_order_status(
    db,
    token
):
    user_id = token["user_id"]

    order = (
        db.query(Order)
        .filter(Order.user_id == user_id)
        .order_by(Order.id.desc())
        .first()
    )

    if not order:
        return "You don't have any orders yet."

    return (
        f"Your latest order #{order.id} "
        f"is currently '{order.status}'."
    )

def get_cancel_order_help(
    db,
    token
):
    user_id = token["user_id"]

    order = (
        db.query(Order)
        .filter(Order.user_id == user_id)
        .order_by(Order.id.desc())
        .first()
    )

    if not order:
        return "No orders found."

    if order.status in [
        "shipped",
        "out_for_delivery",
        "delivered"
    ]:
        return (
            f"Order #{order.id} "
            f"cannot be cancelled because "
            f"it is already {order.status}."
        )

    return (
        f"Order #{order.id} can be cancelled."
    )
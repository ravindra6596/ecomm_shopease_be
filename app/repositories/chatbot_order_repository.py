from app.models.order_model import Order


def get_latest_order_repo(
    db,
    user_id
):
    return (
        db.query(Order)
        .filter(
            Order.user_id == user_id
        )
        .order_by(Order.id.desc())
        .first()
    )


def get_recent_orders_repo(
    db,
    user_id,
    limit=5
):
    return (
        db.query(Order)
        .filter(
            Order.user_id == user_id
        )
        .order_by(Order.id.desc())
        .limit(limit)
        .all()
    )
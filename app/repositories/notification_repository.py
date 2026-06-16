from app.models.notification_model import Notification
from app.models.user_model import User


# create notification repo
def create_notification_repo(
        db,
        user_id,
        title,
        body,
        notification_type,
        reference_id
):
    notification = Notification(
        user_id=user_id,
        title=title,
        body=body,
        notification_type=notification_type,
        reference_id=reference_id
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification

# get notifications repo
def get_notifications_repo(
        db,
        user_id
):
    return db.query(Notification
    ).filter(Notification.user_id == user_id
    ).order_by(Notification.created_at.desc()).all()

# send notification to all users repo
def send_notification_to_all_repo(
        db,
        title,
        body,
        notification_type
):
    users = db.query(User).filter(
        User.is_active == True
    ).all()

    notifications = []

    for user in users:
        notifications.append(
            Notification(
                user_id=user.id,
                title=title,
                body=body,
                notification_type=notification_type,
            )
        )

    db.add_all(notifications)
    db.commit()

    return users


def send_notification_to_selected_users_repo(
        db,
        user_ids,
        title,
        body,
        notification_type,
        reference_id=None
):
    users = db.query(User).filter(
        User.id.in_(user_ids),
        User.is_active == True
    ).all()

    notifications = []

    for user in users:

        notifications.append(
            Notification(
                user_id=user.id,
                title=title,
                body=body,
                notification_type=notification_type,
                reference_id=reference_id
            )
        )

    db.add_all(notifications)
    db.commit()

    return users
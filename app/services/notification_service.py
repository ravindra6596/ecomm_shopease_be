from app.models.notification_model import Notification
from app.models.user_model import User
from app.repositories import notification_repository
from app.utils.firebase_notification import send_push_notification


def send_notification_service(
        db,
        user,
        title,
        body,
        notification_type,
        reference_id
):
    notification_repository.create_notification_repo(
        db,
        user.id,
        title,
        body,
        notification_type,
        reference_id
    )

    if user.fcm_token:

        send_push_notification(
            user.fcm_token,
            title,
            body,
            notification_type,
            reference_id
        )
def send_notification_to_all_users(
        db,
        title,
        body,
        notification_type,
        reference_id
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
                reference_id=reference_id
            )
        )

    # Single DB transaction
    db.add_all(notifications)
    db.commit()

    # Send Push Notifications
    for user in users:

        if not user.fcm_token:
            continue

        try:

            send_push_notification(
                token=user.fcm_token,
                title=title,
                body=body,
                notification_type=notification_type,
                reference_id=reference_id
            )

            print(
                f"✅ Notification sent "
                f"to User {user.id}"
            )

        except Exception as e:

            print(
                f"❌ Failed for User "
                f"{user.id}: {str(e)}"
            )

            # Optional: remove invalid token
            if (
                "registration token" in str(e).lower()
                or
                "requested entity was not found" in str(e).lower()
            ):
                user.fcm_token = None

    db.commit()

# get notifications service
def get_notifications_service(
        db,user_id
):
    return notification_repository.get_notifications_repo(db, user_id)

def send_notification_to_all_service(
        db,
        payload
):

    users = (
        notification_repository
        .send_notification_to_all_repo(
            db=db,
            title=payload.title,
            body=payload.body,
            notification_type=payload.notification_type,
        )
    )

    for user in users:

        if not user.fcm_token:
            continue

        try:

            send_push_notification(
                token=user.fcm_token,
                title=payload.title,
                body=payload.body,
                notification_type=payload.notification_type,
            )

        except Exception as e:

            print(
                f"Failed for user "
                f"{user.id}: {str(e)}"
            )

    return True

# send notification to selected users service
def send_notification_to_selected_users_service(
        db,
        payload
):
    users = (
        notification_repository
        .send_notification_to_selected_users_repo(
            db=db,
            user_ids=payload.user_ids,
            title=payload.title,
            body=payload.body,
            notification_type=payload.notification_type,
        )
    )

    for user in users:

        if not user.fcm_token:
            continue

        try:

            send_push_notification(
                token=user.fcm_token,
                title=payload.title,
                body=payload.body,
                notification_type=payload.notification_type,
            )

        except Exception as e:

            print(
                f"Failed for user "
                f"{user.id}: {str(e)}"
            )

    return True
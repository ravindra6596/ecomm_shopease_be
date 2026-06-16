import firebase_admin
from typing import Optional
from firebase_admin import (
    credentials,
    messaging
)

cred = credentials.Certificate('app/config/firebase-service-account.json')

firebase_admin.initialize_app(cred)


def send_push_notification(
        token: str,
        title: str,
        body: str,
        notification_type: str,
        reference_id: Optional[int] = None
):
    if not token:
        return
    message = messaging.Message(
        token=token,
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        data={
            "notification_type": notification_type,
            "reference_id": str(reference_id),
        }
    )
    messaging.send(message)
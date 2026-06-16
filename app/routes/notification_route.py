from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.database.connection import get_db
from app.schemas.notification_schema import NotificationResponse, SendNotificationToAllSchema, \
    SendNotificationToUsersSchema
from app.schemas.response_schema import CustomResponse
from app.services import notification_service
from app.utils.auth_dependency import verify_token
from app.utils.auth_utils import require_admin
from app.utils.strings import ConstStrings

router = (APIRouter(prefix=ConstStrings.NOTIFICATION_PREFIX, tags=[ConstStrings.NOTIFICATION_TAG]))


@router.post(ConstStrings.GET_POST_ROUTE)
def send_notification_to_all_route(
        payload: SendNotificationToAllSchema,
        db: Session = Depends(get_db),
        token_data: dict = Depends(require_admin)
):
    try:

        notification_service.send_notification_to_all_service(
            db=db,
            payload=payload
        )

        return CustomResponse.success_response(
            statusCode=200,
            message=ConstStrings.NOTIFICATION_SENT,
            data={}
        )

    except HTTPException as e:

        return JSONResponse(
            status_code=e.status_code,
            content=CustomResponse.error_response(
                statusCode=e.status_code,
                message=e.detail,
                error=e.detail,
                data={}
            )
        )


@router.get(ConstStrings.GET_POST_ROUTE)
def get_notifications_route(
        db: Session = Depends(get_db),
        token_data: dict = Depends(
            verify_token
        )
):
    notifications = (
        notification_service.get_notifications_service(
            db,
            token_data[ConstStrings.USER_ID_FIELD]
        )
    )

    notification_data = [
        NotificationResponse.model_validate(
            notification
        ).model_dump()
        for notification in notifications
    ]

    return CustomResponse.success_response(
        statusCode=200,
        message=ConstStrings.NOTIFICATION_FETCHED,
        data=notification_data
    )

# send notification to selected users route
@router.post(ConstStrings.SEND_NOTIFICATION_TO_SELECTED_USERS)
def send_notification_to_selected_users_route(
        payload: SendNotificationToUsersSchema,
        db: Session = Depends(get_db),
        token_data: dict = Depends(require_admin)
):
    try:

        notification_service.send_notification_to_selected_users_service(
            db=db,
            payload=payload
        )

        return CustomResponse.success_response(
            statusCode=200,
            message=ConstStrings.NOTIFICATION_SENT,
            data={}
        )

    except HTTPException as e:

        return JSONResponse(
            status_code=e.status_code,
            content=CustomResponse.error_response(
                statusCode=e.status_code,
                message=e.detail,
                error=e.detail,
                data={}
            )
        )
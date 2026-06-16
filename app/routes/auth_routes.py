from time import time

from fastapi import APIRouter, Depends, HTTPException, Request, FastAPI
from slowapi import Limiter
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.config.config import settings
from app.core.event_logger import log_event
from app.core.log_events import UserEvent
from app.database.connection import get_db
from app.schemas.auth_schema import UserCreate, UserResponse, UserLogin
from app.schemas.response_schema import CustomResponse

from app.services import auth_service
from app.utils.auth_dependency import verify_token
from app.utils.auth_utils import create_access_token
from app.utils.strings import ConstStrings

router = APIRouter(prefix=ConstStrings.AUTH_PREFIX, tags=[ConstStrings.AUTH_TAG])
app = FastAPI()


# register route
@router.post(ConstStrings.REGISTER_ROUTE, response_model=dict)
def register_route(
        emp: UserCreate,
        db: Session = Depends(get_db),
):
    try:
        db_user = (auth_service.register_service(db, emp))

        user_data = UserResponse.model_validate(
            db_user
        )
        log_event(
            UserEvent.REGISTERED.value,
            {
                "id": user_data.id,
                "name": user_data.name,
                "email": user_data.email,
                "role": user_data.role,
                "created_at": user_data.created_at.strftime("%d-%m-%Y %H:%M:%S")
            }
        )

        return CustomResponse.success_response(
            statusCode=201,
            data={},
            message=ConstStrings.USER_REGISTER
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


# Rate limiter for wrong password
limiter = Limiter(key_func=lambda request: request.client.host)  # use IP as key

failed_attempts = {}


# Login routes
@router.post(ConstStrings.LOGIN_ROUTE, response_model=dict)
def login_route(
        request: Request,
        user: UserLogin,
        db: Session = Depends(get_db)
):
    ip = request.client.host

    if ip not in failed_attempts:
        failed_attempts[ip] = {"count": 0, "time": time()}

    record = failed_attempts[ip]

    #  block if exceeded
    if record["count"] >= settings.login_max_attempts:
        if time() - record["time"] < settings.rate_block_time:
            return JSONResponse(
                status_code=429,
                content=CustomResponse.error_response(
                    statusCode=429,
                    error=ConstStrings.RATE_EXCEEDED,
                    message=ConstStrings.TOO_MANY,
                    data={}
                )
            )
        else:
            record["count"] = 0  # reset after timeout

    try:
        result = auth_service.login_service(
            db,
            user.email,
            user.password,
            user.guest_id,
            user.fcm_token
        )

        #  reset on success
        failed_attempts.pop(ip, None)

        return CustomResponse.success_response(
            statusCode=200,
            message=ConstStrings.LOGIN_SUCCESS,
            data=result
        )

    except HTTPException as e:
        # only count wrong password
        if e.status_code == 401:
            record["count"] += 1
            record["time"] = time()

        return JSONResponse(
            status_code=e.status_code,
            content=CustomResponse.error_response(
                statusCode=e.status_code,
                error=e.detail,
                message=e.detail,
                data={}
            )
        )


@router.post(ConstStrings.REFRESH_TOKEN_ROUTE)
def refresh_token_route(refresh_token: str):
    result = auth_service.refresh_access_token(refresh_token)
    new_access_token = create_access_token({
        "user_id": result["user_id"],
        "email": result["email"],
        "role":result["role"]
    })
    return CustomResponse.success_response(
        statusCode=200,
        message=ConstStrings.NEW_ACCESS_TOKEN,
        data={
            "user_id": result["user_id"],
            "email": result["email"],
            "access_token": new_access_token
        }
    )


# logout
@router.post(ConstStrings.LOGOUT_ROUTE)
def logout(
        token_data: dict = Depends(verify_token),
        db: Session = Depends(get_db)
):
    auth_service.logout_service(
        db,
        token_data["raw_token"]
    )

    return CustomResponse.success_response(
        statusCode=200,
        message=ConstStrings.LOGOUT_SUCCESS,
        data={}
    )

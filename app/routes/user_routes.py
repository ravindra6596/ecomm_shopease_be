from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.database.connection import get_db
from app.schemas.auth_schema import UserResponse, UserDetailsResponse
from app.schemas.response_schema import CustomResponse
from app.services import user_service
from app.schemas.auth_schema import UserUpdate
from app.utils.enums import SearchField, SortField, SortOrder
from app.utils.auth_dependency import verify_token
from app.utils.auth_utils import require_admin
from app.utils.strings import ConstStrings

router = APIRouter(prefix=ConstStrings.USERS_PREFIX, tags=[ConstStrings.USERS_TAG])


# List of user route
@router.get(ConstStrings.GET_POST_ROUTE, response_model=dict)
def get_users_route(
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1),
        search: str = None,
        search_filter: SearchField = SearchField.id,
        sort_by: SortField = SortField.id,
        order: SortOrder = SortOrder.desc,
        db: Session = Depends(get_db),
        token_data: dict = Depends(require_admin)
):
    result = user_service.get_users_service(
        db=db,
        page=page,
        limit=limit,
        search=search,
        search_filter=search_filter,
        sort_by=sort_by,
        order=order,
        token_data=token_data
    )

    return CustomResponse.success_response(
        statusCode=200,
        message=ConstStrings.USER_FETCHED,
        data=result
    )


# get profile repo
@router.get(ConstStrings.USERS_PROFILE)
def get_profile(
        db: Session = Depends(get_db),
        token_data: dict = Depends(verify_token)
):
    result = user_service.get_profile_service(db, token_data)

    return CustomResponse.success_response(
        statusCode=200,
        message=ConstStrings.USER_FETCHED,
        data=UserResponse.model_validate(result)
    )


# Get user by id route
@router.get(ConstStrings.ID_ROUTE)
def get_user_by_id(id: int, db: Session = Depends(get_db),token:dict = Depends(verify_token)):
    result = user_service.get_user_by_id(db, id,token)
    if not result:
        return CustomResponse.error_response(
            statusCode=404,
            error=ConstStrings.USER_NOT_FOUND,
            message=ConstStrings.USER_NOT_FOUND,
            data={ConstStrings.USER_ID_FIELD: id}
        )

    return CustomResponse.success_response(
        statusCode=200,
        message=ConstStrings.USER_FETCHED,
        data=UserDetailsResponse.model_validate(result)
    )


# Update User route
@router.patch(ConstStrings.ID_ROUTE)
def update_employee_route(
        user: UserUpdate,
        db: Session = Depends(get_db),
        token_data: dict = Depends(verify_token)
):

    updated_user = (
        user_service.update_user_service(db,  user, token_data)
    )

    if not updated_user:
        return CustomResponse.error_response(
            statusCode=404,
            error=ConstStrings.USER_NOT_FOUND,
            message=ConstStrings.USER_NOT_FOUND,
            data={}
        )

    return CustomResponse.success_response(
        statusCode=200,
        message=ConstStrings.USER_UPDATED,
        data=UserResponse.model_validate(
            updated_user
        )
    )


# delete user route
@router.delete(ConstStrings.ID_ROUTE)
def delete_user(
        user_id: int,
        db: Session = Depends(get_db),
        token: dict = Depends(require_admin)
):
    result = user_service.delete_user_service(
        db,
        user_id, token
    )

    if not result:
        return CustomResponse.error_response(
            statusCode=404,
            error=ConstStrings.USER_NOT_FOUND,
            message=ConstStrings.USER_NOT_FOUND,
            data={ConstStrings.USER_ID_FIELD: user_id}
        )

    return CustomResponse.success_response(
        statusCode=200,
        message=ConstStrings.USER_DELETED,
        data={ConstStrings.USER_ID_FIELD: user_id}
    )

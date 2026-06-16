from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.database.connection import get_db
from app.schemas.response_schema import CustomResponse
from app.schemas.wishlist_schema import AddWishlistSchema, WishlistResponse
from app.services import wishlist_service
from app.utils.auth_dependency import verify_token
from app.utils.strings import ConstStrings

router = APIRouter(prefix=ConstStrings.WISHLIST_PREFIX, tags=[ConstStrings.WISHLIST_TAG])
# Add Wishlist
@router.post(ConstStrings.GET_POST_ROUTE)
def add_wishlist_route(
    payload: AddWishlistSchema,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):

    try:
        wishlist = (
            wishlist_service.add_wishlist_service(
                db,
                payload,
                token_data
            )
        )

        return CustomResponse.success_response(
            statusCode=201,
            message=ConstStrings.WISHLIST_ADDED,
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
# Get Wishlist
@router.get(ConstStrings.GET_POST_ROUTE)
def get_wishlist_route(
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):

    wishlist = (
        wishlist_service.get_wishlist_service(
            db,
            token_data
        )
    )

    response = [
        WishlistResponse(
            id=item.id,
            product_id=item.product.id,
            product_name=item.product.name,
            product_price=item.product.price,
            created_at=item.created_at
        )
        for item in wishlist
    ]

    return CustomResponse.success_response(
        statusCode=200,
        message=ConstStrings.WISHLIST_FETCHED,
        data=response
    )
# Clear Wishlist
@router.delete("/clear")
def clear_wishlist_route(
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):

    try:

        wishlist_service.clear_wishlist_service(
            db,
            token_data
        )

        return CustomResponse.success_response(
            statusCode=200,
            message=ConstStrings.WISHLIST_CLEARED,
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


# Remove Wishlist
@router.delete(ConstStrings.ID_ROUTE)
def remove_wishlist_route(
    id: int,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):

    try:

        wishlist_service.remove_wishlist_service(
            db,
            id,
            token_data
        )

        return CustomResponse.success_response(
            statusCode=200,
            message=ConstStrings.WISHLIST_REMOVED,
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
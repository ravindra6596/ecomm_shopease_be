# Add To Cart


from fastapi import Depends, HTTPException, APIRouter, Query, Header, Request
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.core.event_logger import log_event
from app.core.log_events import CartEvent
from app.database.connection import get_db
from app.schemas.cart_schema import AddToCartSchema, CartResponse, UpdateCartQuantitySchema, GetCartResponse
from app.schemas.response_schema import CustomResponse
from app.services import cart_service
from app.utils.auth_dependency import verify_token, optional_verify_token
from app.utils.auth_utils import require_admin
from app.utils.enums import SortOrder, CartSortField
from app.utils.strings import ConstStrings

router = APIRouter(prefix=ConstStrings.CART_PREFIX, tags=[ConstStrings.CART_TAG])
@router.post(ConstStrings.GET_POST_ROUTE)
def add_to_cart_route_old(
    payload: AddToCartSchema,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    try:

        cart = cart_service.add_to_cart_service(
            db,
            payload,
            token_data
        )

        user_id = token_data.get(
            ConstStrings.USER_ID_FIELD
        )

        log_event(
            CartEvent.CREATED.value,
            {
                "user_id": user_id,
                "product_id": payload.product_id,
                "quantity": 1,
            }
        )

        return CustomResponse.success_response(
            statusCode=201,
            data={},
            message=ConstStrings.CART_CREATED,
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

@router.post(ConstStrings.GET_POST_ROUTE)
def add_to_cart_route_new(
    payload: AddToCartSchema,
    request: Request,
    guest_id: str = Header(default=None,alias="guest-id"),
    token_data: dict = Depends(optional_verify_token),
    db: Session = Depends(get_db)
):

    try:

        user_id = None

        if token_data:
            user_id = token_data.get(
                ConstStrings.USER_ID_FIELD
            )

        # VALIDATION
        if not user_id and not guest_id:

            raise HTTPException(
                status_code=400,
                detail="guest_id required"
            )

        cart = cart_service.add_to_cart_service(
            db=db,
            payload=payload,
            user_id=user_id,
            guest_id=guest_id
        )

        return CustomResponse.success_response(
            statusCode=201,
            data={},
            message=ConstStrings.CART_CREATED
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
# Get All Admin Carts
@router.get(ConstStrings.ADMIN_ROUTE)
def get_all_admin_carts_route(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    search: str = Query(None),
    sort_by: CartSortField = CartSortField.id,
    order: SortOrder = SortOrder.desc,
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_admin)
):

    result = cart_service.get_all_admin_carts_service(
        db=db,
        page=page,
        limit=limit,
        search=search,
        sort_by=sort_by,
        order=order.value,
    )

    log_event(
        CartEvent.LISTED.value,
        {
            "count": len(result["items"]),
            "page": page,
            "limit": limit,
        }
    )

    return CustomResponse.success_response(
        statusCode=200,
        message=ConstStrings.CART_FETCHED,
        data=result
    )


# Get Cart Items
@router.get(ConstStrings.GET_POST_ROUTE)
def get_cart_items_route(
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):

    cart_items = cart_service.get_cart_items_service(
        db=db,
        token=token_data,
    )

    response = [
        CartResponse(
            id=item.id,
            cart_id=item.cart_id,
            product_id=item.product_id,
            quantity=item.quantity,
            product_name=item.product.name,
            product_price=item.product.price,
            total_price=item.product.price * item.quantity,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )
        for item in cart_items
    ]

    log_event(
        CartEvent.LISTED.value,
        {
            "count": len(response),
            "result": response
        }
    )
    grand_total = sum(
        item.product.price * item.quantity
        for item in cart_items
    )

    total_items = sum(
        item.quantity
        for item in cart_items
    )
    return CustomResponse.success_response(
        statusCode=200,
        message=ConstStrings.CART_FETCHED,
        data={
            "grand_total": grand_total,
            "total_items": total_items,
            "items": response,
        }
    )

# Get Cart By id
@router.get(ConstStrings.ID_ROUTE)
def get_cart_by_id_route(
    id: int,
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_admin)
):

    try:

        cart = cart_service.get_cart_by_id_service(
            db,
            id,
            token_data
        )
        log_event(
            CartEvent.FETCHED.value,
            {
                "id": id,

            }
        )
        return CustomResponse.success_response(
            statusCode=200,
            message=ConstStrings.CART_FETCHED,
            data=GetCartResponse.model_validate(cart),
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

# Update Cart Quantity
@router.patch(ConstStrings.ID_ROUTE)
def update_cart_quantity_route(
    id: int,
    payload: UpdateCartQuantitySchema,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):

    try:

        cart_item = (
            cart_service.update_cart_quantity_service(
                db,
                id,
                payload,
                token_data
            )
        )

        total_price = (
            cart_item.product.price *
            cart_item.quantity
        )

        log_event(
            CartEvent.UPDATED.value,
            {
                "cart_item_id": cart_item.id,
                "quantity": cart_item.quantity,
                "total_price": total_price,
            }
        )

        return CustomResponse.success_response(
            statusCode=200,
            message=ConstStrings.CART_UPDATED,
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

# Clear Cart
@router.delete(ConstStrings.CART_CLEAR)
def clear_cart_route(
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):

    try:

        cart_service.clear_cart_service(
            db,
            token_data
        )

        log_event(
            CartEvent.DELETED.value,
            {
                "user_id": token_data.get(
                    ConstStrings.USER_ID_FIELD
                )
            }
        )

        return CustomResponse.success_response(
            statusCode=200,
            message=ConstStrings.CART_DELETED,
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


# Remove Cart Item
@router.delete(ConstStrings.ID_ROUTE)
def remove_cart_item_route(
    id: int,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):

    try:

        cart_service.remove_cart_item_service(
            db,
            id,
            token_data
        )

        log_event(
            CartEvent.DELETED.value,
            {
                "id": id
            }
        )

        return CustomResponse.success_response(
            statusCode=200,
            message=ConstStrings.CART_ITEM_REMOVED,
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
######### NEW CART ###########

@router.get("/test-guest")
def test_guest():
    return {
        "success": True,
        "message": "Guest route works",
        "data": {}
    }
@router.get("/ping")
def ping():
    return {"ok": True}
@router.get("/cart-new")
def get_cart_items_route_new(
    db: Session = Depends(get_db),
    token_data: dict = Depends(optional_verify_token),
    guest_id: str = Header(default=None, alias="X-Guest-Id")
):
    print("TOKEN:", token_data)
    print("GUEST ID:", guest_id)

    # If neither token nor guest_id is provided, return an empty cart
    # instead of raising an error — the route is designed to support
    # both authenticated users and guest users.
    if not token_data and not guest_id:
        return CustomResponse.success_response(
            statusCode=200,
            message=ConstStrings.CART_FETCHED,
            data={
                "grand_total": 0,
                "total_items": 0,
                "items": []
            }
        )

    cart_items = cart_service.get_cart_items_service_new(
        db,
        token_data,
        guest_id
    )

    grand_total = sum(
        item.product.price * item.quantity
        for item in cart_items
    )

    total_items = sum(
        item.quantity
        for item in cart_items
    )

    return CustomResponse.success_response(
        statusCode=200,
        message=ConstStrings.CART_FETCHED,
        data={
            "grand_total": grand_total,
            "total_items": total_items,
            "items": cart_items
        }
    )

@router.patch("/cart-new/{id}")
def update_cart_quantity_route_new(
    id: int,
    payload: UpdateCartQuantitySchema,
    db: Session = Depends(get_db),
    token_data: dict = Depends(optional_verify_token),
    guest_id: str = Header(default=None)
):

    cart_item = cart_service.update_cart_quantity_service_new(
        db,
        id,
        payload,
        token_data,
        guest_id
    )

    return CustomResponse.success_response(
        statusCode=200,
        message="Cart updated",
        data={}
    )

@router.delete("/cart-new/{id}")
def remove_cart_item_route_new(
    id: int,
    db: Session = Depends(get_db),
    token_data: dict = Depends(optional_verify_token),
    guest_id: str = Header(default=None)
):

    cart_service.remove_cart_item_service_new(
        db,
        id,
        token_data,
        guest_id
    )

    return CustomResponse.success_response(
        statusCode=200,
        message="Item removed",
        data={}
    )

@router.delete("/cart-new/clear")
def clear_cart_route_new(
    db: Session = Depends(get_db),
    token_data: dict = Depends(optional_verify_token),
    guest_id: str = Header(default=None)
):

    try:

        deleted_count = cart_service.clear_cart_service_new(
            db,
            token_data,
            guest_id
        )

        return CustomResponse.success_response(
            statusCode=200,
            message="Cart cleared successfully",
            data={
                "deleted_items": deleted_count
            }
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
# Create Order
from datetime import timedelta, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse, StreamingResponse

from app.core.event_logger import log_event
from app.core.log_events import OrderEvent
from app.database.connection import get_db
from app.schemas.order_schema import CreateOrderSchema, OrderResponse, OrderItemResponse, UpdateOrderAddressSchema, \
    UpdateOrderStatusSchema, UpdatePaymentStatusSchema, OrderCreateResponse
from app.schemas.response_schema import CustomResponse
from app.services import order_service
from app.utils.auth_dependency import verify_token
from app.utils.auth_utils import require_admin
from app.utils.enums import SortOrder, OrderSortField, OrderStatus, PaymentStatus, PaymentMethod
from app.utils.strings import ConstStrings
from app.utils.url_helper import build_image_url

router = APIRouter(prefix=ConstStrings.ORDER_PREFIX, tags=[ConstStrings.ORDER_TAG])


# Create Order
@router.post(ConstStrings.GET_POST_ROUTE)
def create_order_route(
        payload: CreateOrderSchema,
        db: Session = Depends(get_db),
        token_data: dict = Depends(verify_token)
):
    try:

        order = order_service.create_order_service(
            db,
            payload,
            token_data
        )

        log_event(
            OrderEvent.CREATED.value,
            {
                "order_id": order.id,
                "user_id": order.user_id,
                "address_id": order.address_id,
                "total_amount": order.total_amount,
                "status": order.status,
                "payment_status": order.payment_status,
            }
        )

        response_data = OrderCreateResponse(
            order_id=order.id,
            payment_method=order.payment_method,
            order_date=order.created_at,
            delivery_date=order.delivery_date,
        )
        return CustomResponse.success_response(
            statusCode=201,
            message=ConstStrings.ORDER_CREATED,
            data=response_data.model_dump(),
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


# Get Orders
@router.get(ConstStrings.GET_POST_ROUTE)
def get_orders_route(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    search: str = Query(None),
    order_status: Optional[OrderStatus] = Query(None),
    payment_status: Optional[PaymentStatus] = Query(None),
    payment_method: Optional[PaymentMethod] = Query(None),
    sort_by: OrderSortField = OrderSortField.id,
    order: SortOrder = SortOrder.desc,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):

    result = order_service.get_orders_service(
        db=db,
        token=token_data,
        page=page,
        limit=limit,
        search=search,
        order_status=order_status.value if order_status else None,
        payment_status=payment_status.value if payment_status else None,
        payment_method=payment_method.value if payment_method else None,
        sort_by=sort_by,
        order=order.value,
    )

    log_event(
        OrderEvent.LISTED.value,
        {
            "count": len(result["items"]),
            "page": page,
            "limit": limit,
            "result": result
        }
    )

    return CustomResponse.success_response(
        statusCode=200,
        message=ConstStrings.ORDER_FETCHED,
        data=result
    )
# Get Order By id
@router.get(ConstStrings.ID_ROUTE)
def get_order_by_id_route(
    id: int,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):

    try:

        order = order_service.get_order_by_id_service(
            db,
            id,
            token_data
        )

        response = OrderResponse(
            id=order.id,
            user_name=order.user.name,
            user_id=order.user_id,
            address_id=order.address_id,
            total_amount=order.total_amount,
            status=order.status,
            payment_status=order.payment_status,
            payment_method=order.payment_method,
            created_at=order.created_at,
            updated_at=order.updated_at,
            delivery_date=order.delivery_date,
            items=[
                OrderItemResponse(
                    product_id=item.product_id,
                    product_name=item.product.name,
                    image_url = build_image_url(item.product.images[0].image_url) if item.product.images else None,
                    quantity=item.quantity,
                    price=item.price,
                    total_price=item.quantity * item.price
                )
                for item in order.items
            ],
            address=order.address,
        )

        return CustomResponse.success_response(
            statusCode=200,
            message=ConstStrings.ORDER_FETCHED,
            data=response
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

# Update Order Address
@router.patch(ConstStrings.ORDER_ADDRESS)
def update_order_address_route(
    id: int,
    payload: UpdateOrderAddressSchema,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):

    try:

        order_service.update_order_address_service(
            db,
            id,
            payload,
            token_data
        )

        return CustomResponse.success_response(
            statusCode=200,
            message=ConstStrings.ADDRESS_UPDATED,
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

# Cancel Order
@router.patch(ConstStrings.ORDER_CANCEL)
def cancel_order_route(
    id: int,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):

    try:

        order_service.cancel_order_service(
            db,
            id,
            token_data
        )

        return CustomResponse.success_response(
            statusCode=200,
            message=ConstStrings.ORDER_CANCELLED,
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

# Update Order Status
@router.patch(ConstStrings.ORDER_STATUS)
def update_order_status_route(
    id: int,
    payload: UpdateOrderStatusSchema,
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_admin)
):

    try:

        order = order_service.update_order_status_service(
            db,
            id,
            payload
        )
        log_event(
            OrderEvent.CREATED.value,
            {
                "order_id": order.id,
                "user_id": order.user_id,
                "payment_method": order.payment_method,
                "payment_status": order.payment_status,
                "status": order.status,
            }
        )
        return CustomResponse.success_response(
            statusCode=200,
            message=ConstStrings.ORDER_STATUS_UPDATED,
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

# Update Payment Status
@router.patch(ConstStrings.ORDER_PAYMENT)
def update_payment_status_route(
    id: int,
    payload: UpdatePaymentStatusSchema,
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_admin)
):

    try:

        order_service.update_payment_status_service(
            db,
            id,
            payload
        )

        return CustomResponse.success_response(
            statusCode=200,
            message=ConstStrings.PAYMENT_STATUS_UPDATED,
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

@router.get(ConstStrings.ORDER_INVOICE)
def download_invoice(
    id: int,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):

    pdf = order_service.download_invoice_service(
        db,
        id,
        token_data
    )

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            f"attachment; filename=ShopEase_Invoice_{id}.pdf"
        }
    )
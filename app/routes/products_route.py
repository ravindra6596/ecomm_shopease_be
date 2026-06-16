from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Form, File, UploadFile
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.core.log_events import ProductEvent
from app.utils.auth_utils import require_admin
from app.utils.strings import ConstStrings
from app.core.event_logger import log_event
from app.database.connection import get_db
from app.schemas.product_schema import ProductCreate, ProductResponse, ProductUpdate
from app.services import product_service
from app.utils.auth_dependency import verify_token
from app.utils.enums import ProductSortField, SortOrder
from app.schemas.response_schema import CustomResponse

router = APIRouter(prefix=ConstStrings.PRODUCT_PREFIX, tags=[ConstStrings.PRODUCT_TAG])


@router.post(ConstStrings.GET_POST_ROUTE)
def create_products_route(
    name: str = Form(...),
    description: str = Form(None),
    price: float = Form(...),
    category_id: int = Form(...),
    discount: float = Form(0),
    return_policy: str = Form(None),
    images: List[UploadFile] = File([]),   # optional like your old images
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_admin),
):
    try:
        payload = ProductCreate(
            name=name,
            description=description,
            price=price,
            category_id=category_id,
            discount=discount,
            return_policy=return_policy
        )

        create_products = product_service.create_product_service(
            db,
            payload,
            images,
            token_data
        )
        user_id = token_data.get("user_id")

        log_event(
            ProductEvent.CREATED.value,
            {
                 "name": payload.name,
                "price": payload.price,
                "category_id": payload.category_id,
                "description": payload.description,
                "images": [img.filename for img in images],
                "user_id": user_id,

            }
        )

        return CustomResponse.success_response(
            statusCode=201,
            message=ConstStrings.PRODUCT_CREATED,
            data={}
        )

    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content=CustomResponse.error_response(
                statusCode=e.status_code,
                message=e.detail,
                error=str(e),
                data={}
            )
        )

# List of products route
@router.get(ConstStrings.GET_POST_ROUTE, response_model=dict)
def get_products_route(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    search: str = None,
    category_id: int = None,
    min_price: float = None,
    max_price: float = None,
    sort_by: ProductSortField = ProductSortField.id,
    order: SortOrder = SortOrder.desc,
    db: Session = Depends(get_db),
):

    result = product_service.get_products_service(
        db=db,
        page=page,
        limit=limit,
        search=search,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        order=order,
    )
    log_event(
        ProductEvent.LISTED.value,
        {
            "count": len(result),
            "page": page,
            "limit": limit,
            "filters": {
                "search": search,
                "category_id": category_id
            },
            "result": result
        }
    )
    return CustomResponse.success_response(
        statusCode=200,
        message=ConstStrings.PRODUCTS_FETCHED,
        data=result
    )


# Get product by id route
@router.get(ConstStrings.ID_ROUTE)
def get_product_by_id( id: int, db: Session = Depends(get_db)):
    result = product_service.get_product_by_id(db,  id)
    if not result:
        return CustomResponse.error_response(
            statusCode=404,
            error=None,
            message=ConstStrings.NO_PRODUCT,
            data={}
    )
    log_event(
        ProductEvent.FETCHED.value,
        {
            "id": result.id,
            "name": result.name,
            "is_deleted": result.is_deleted,
            "deleted_by": result.deleted_by,
            "created_at": result.created_at,
            "updated_at": result.updated_at,
        }
    )
    return CustomResponse.success_response(
        statusCode=200,
        message=ConstStrings.PRODUCTS_FETCHED,
        data=ProductResponse.model_validate(result)
    )


# Update product route
@router.patch(ConstStrings.ID_ROUTE)
def update_product_route(
    id: int,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    category_id: Optional[int] = Form(None),
    images: Optional[List[UploadFile]] = File(None),  # Accept file uploads for images
    db: Session = Depends(get_db),
    discount: float = Form(0),
    return_policy: str = Form(None),
    token_data: dict = Depends(require_admin)
):
    product_data = ProductUpdate(
        name=name,
        description=description,
        price=price,
        category_id=category_id,
        discount=discount,
        return_policy=return_policy
    )

    updated_product = product_service.update_product_service(
        db,
        id,
        product_data,
        images,token_data
    )

    if not updated_product:
        return CustomResponse.error_response(
            statusCode=404,
            message=ConstStrings.NO_PRODUCT,
            error=None,
            data={}
        )

    log_event(
        ProductEvent.UPDATED.value,
        {
            "id": updated_product.id,
            "changes": updated_product,
        }
    )

    return CustomResponse.success_response(
        statusCode=200,
        message=ConstStrings.PRODUCT_UPDATED,
        data={}
    )

@router.delete(ConstStrings.ID_ROUTE)
def soft_delete_product_route(
    id: int,
    db: Session = Depends(get_db),token_data: dict = Depends(verify_token)
):

    deleted_product = product_service.soft_delete_product_service(
        db,
        id,token_data
    )
    log_event(
        ProductEvent.DELETED.value,
        {
            "id": deleted_product.id,
            "changes": ProductResponse.model_validate(deleted_product),
        }
    )
    return CustomResponse.success_response(
        statusCode=200,
        message=ConstStrings.PRODUCT_DELETED,
        data={}
    )

@router.post(ConstStrings.BULK_PRODUCT_ROUTE)
def create_products_bulk(
    payload: List[ProductCreate],
    db: Session = Depends(get_db),
        token_data: dict = Depends(verify_token)
):
    try:
        products = product_service.create_products_bulk_service(db, payload, token_data)

        data = [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "price": p.price,
                "category_id": p.category_id,
                "created_at": p.created_at,
                "updated_at": p.updated_at
            }
            for p in products
        ]
        log_event(
            ProductEvent.CREATED.value,
            {
                "count": len(products),
                "ids": [c.id for c in products],
                "data": data
            }
        )
        return CustomResponse.success_response(
            statusCode=201,
            message=ConstStrings.MULTI_PRODUCTS_CREATED,
            data={}
        )

    except HTTPException as e:
        return CustomResponse.error_response(
            statusCode=e.status_code,
            message=e.detail,
            error=str(e),
            data={}
        )

    except Exception as e:
        return CustomResponse.error_response(
            statusCode=500,
            message=ConstStrings.INTERNAL_SERVER_ERROR,
            error=str(e),
            data={}
        )

# Delete Product Image
@router.delete("/images/{id}")
def delete_product_image_route(
    id: int,
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_admin)
):

    try:

        product_service.delete_product_image_service(
            db,
            id
        )

        return CustomResponse.success_response(
            statusCode=200,
            message=ConstStrings.IMAGE_DELETED,
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
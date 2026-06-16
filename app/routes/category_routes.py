from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Form, File, UploadFile
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.core.log_events import CategoryEvent
from app.utils.auth_utils import require_admin
from app.utils.strings import ConstStrings
from app.core.event_logger import log_event
from app.database.connection import get_db
from app.schemas.category_schema import CategoryCreate, CategoryResponse, CategoryUpdate, CategoryByIdResponse
from app.services import category_service
from app.schemas.response_schema import CustomResponse
from app.utils.enums import CategorySortField, SortOrder

router = APIRouter(prefix=ConstStrings.CATEGORY_PREFIX, tags=[ConstStrings.CATEGORY_TAG])

# create category
@router.post(ConstStrings.GET_POST_ROUTE)
def create_category(
    name: str = Form(...),
    images: List[UploadFile] = File([]),
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_admin)
):
    try:
        payload = CategoryCreate(name=name)
        category = category_service.create_category_service(db, payload, images, token_data)
        user_id = token_data.get(ConstStrings.USER_ID_FIELD)
        log_event(
            CategoryEvent.CREATED.value,
            {
                "id": category.id,
                "name": category.name,
                "created_by": user_id,
                "created_at": category.created_at.isoformat(),
            }
        )
        return CustomResponse.success_response(
            statusCode=201,
            data={},
            message=ConstStrings.CATEGORY_CREATED,
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

# all categories list
@router.get(ConstStrings.GET_POST_ROUTE)
def get_categories(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    search: str = Query(None),
    sort_by: CategorySortField = CategorySortField.id,
    order: SortOrder = SortOrder.desc,
    db: Session = Depends(get_db),
):
    result = category_service.get_category_service(
        db=db,
        page=page,
        limit=limit,
        search=search,
        sort_by=sort_by.value,
        order=order.value,
    )
    log_event(
        CategoryEvent.LISTED.value,
        {
            "count": len(result),
            "page": page,
            "limit": limit,
            "result": result
        }
    )
    return CustomResponse.success_response(
        statusCode=200,
        message=ConstStrings.CATEGORY_FETCHED,
        data=result
    )
# Top Categories
@router.get(ConstStrings.TOP_CATEGORY_ROUTE)
def get_top_categories(
    db: Session = Depends(get_db),
    # token_data: dict = Depends(require_admin)
):

    result = category_service.get_top_categories_service(
        db,
    )

    return CustomResponse.success_response(
        statusCode=200,
        message="Top categories fetched successfully",
        data=result
    )

# bulk category routes
@router.post(ConstStrings.BULK_CATEGORY_ROUTE)
def create_category_bulk(
    payload: List[CategoryCreate],
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_admin)
):
    try:
        categories = category_service.create_category_bulk_service(
            db,
            payload,
            token_data
        )

        data =[
            {
                "id": c.id,
                "name": c.name
            }
            for c in categories
        ]
        log_event(
            CategoryEvent.BULK_CREATED.value,
            {
                "count": len(categories),
                "ids": [c.id for c in categories],
                "data": data
            }
        )
        return CustomResponse.success_response(
            statusCode=201,
            message=ConstStrings.MULTI_CATEGORY_CREATED,
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

# Get category by id route
@router.get(ConstStrings.ID_ROUTE)
def get_category_by_id(
    id: int,
    db: Session = Depends(get_db),
):

    category = category_service.get_category_by_id_service(db, id)

    return CustomResponse.success_response(
        statusCode=200,
        message=ConstStrings.CATEGORY_FETCHED,
        data=CategoryByIdResponse.model_validate(category),
    )


# update category route
@router.patch(ConstStrings.ID_ROUTE)
def update_category(
    id: int,
    name: Optional[str] = Form(None),
    images: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_admin)
):
    try:
        payload = CategoryUpdate(name=name)
        updated = category_service.update_category_service(db, id, payload, images, token_data)
        log_event(
            CategoryEvent.UPDATED.value,
            {
                "id": updated.id,
                "changes": CategoryResponse.model_validate(updated),
            }
        )
        return CustomResponse.success_response(
            statusCode=200,
            message=ConstStrings.CATEGORY_UPDATED,
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

# category delete route
@router.delete(ConstStrings.ID_ROUTE)
def delete_category_route(
    id: int,
    db: Session = Depends(get_db),token_data: dict = Depends(require_admin)
):

    deleted = category_service.delete_category_service(db, id,token_data)
    user_id = token_data.get(ConstStrings.USER_ID_FIELD)
    log_event(
        CategoryEvent.DELETED.value,
        {
            "id": deleted.id,
            "deleted_by": user_id
        }
    )
    return CustomResponse.success_response(
        statusCode=200,
        message=ConstStrings.CATEGORY_DELETED,
        data={}
    )


# Delete Category Image
@router.delete("/images/{id}")
def delete_category_image_route(
    id: int,
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_admin)
):
    try:
        category_service.delete_category_image_service(
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
from typing import Optional

from fastapi import Depends, File, Form, UploadFile, APIRouter
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.banners_schema import BannerCreate, BannerUpdate
from app.schemas.response_schema import CustomResponse
from app.services import banners_service
from app.utils.auth_dependency import get_optional_user
from app.utils.auth_utils import require_admin
from app.utils.strings import ConstStrings

router = APIRouter(prefix=ConstStrings.BANNER_PREFIX, tags=[ConstStrings.BANNER_TAG])
@router.post(ConstStrings.GET_POST_ROUTE)
def create_banner_route(
    title: str = Form(...),
    description: str = Form(None),
    category_id: int = Form(None),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_admin)
):

    payload = BannerCreate(
        title=title,
        description=description,
        category_id=category_id
    )

    banners_service.create_banner_service(
        db,
        payload,
        image,
        token_data
    )

    return CustomResponse.success_response(
        statusCode=201,
        message="Banner Created",
        data={}
    )

@router.get(ConstStrings.GET_POST_ROUTE)
def get_banners_route(
    category_id: Optional[int] = None,
    db: Session = Depends(get_db),
    token_data: dict = Depends(get_optional_user)
):

    banners = (
        banners_service
        .get_banners_service(
            db,
            category_id,
            token_data
        )
    )

    return CustomResponse.success_response(
        statusCode=200,
        message="Banners fetched successfully",
        data=banners
    )

@router.get(ConstStrings.ID_ROUTE)
def get_banner_by_id_route(
    id: int,
    db: Session = Depends(get_db)
):

    banner = (
        banners_service
        .get_banner_by_id_service(
            db,
            id
        )
    )

    return CustomResponse.success_response(
        statusCode=200,
        message="Banner fetched successfully",
        data=banner
    )

@router.patch(ConstStrings.ID_ROUTE)
def update_banner_route(
    id: int,

    title: Optional[str] = Form(None),

    description: Optional[str] = Form(None),

    category_id: Optional[int] = Form(None),

    is_active: Optional[bool] = Form(None),

    image: UploadFile = File(None),

    db: Session = Depends(get_db),

    token_data: dict = Depends(
        require_admin
    )
):

    payload = BannerUpdate(
        title=title,
        description=description,
        category_id=category_id,
        is_active=is_active
    )

    banners_service.update_banner_service(
        db,
        id,
        payload,
        image
    )

    return CustomResponse.success_response(
        statusCode=200,
        message="Banner updated successfully",
        data={}
    )

@router.delete(ConstStrings.ID_ROUTE)
def delete_banner_route(
    id: int,
    db: Session = Depends(get_db),
    token_data: dict = Depends(
        require_admin
    )
):

    banners_service.delete_banner_service(
        db,
        id
    )

    return CustomResponse.success_response(
        statusCode=200,
        message="Banner deleted successfully",
        data={}
    )
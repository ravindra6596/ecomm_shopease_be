from typing import Optional

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.models import Category
from app.repositories import banner_repository
from app.schemas.banners_schema import BannerCreate, BannerUpdate, BannerResponse
from app.utils.url_helper import build_image_url


def create_banner_service(
    db: Session,
    payload: BannerCreate,
    image: UploadFile,
    token: dict
):

    if payload.category_id:

        category = (
            db.query(Category)
            .filter(
                Category.id ==
                payload.category_id,
                Category.is_deleted == False
            )
            .first()
        )

        if not category:

            raise HTTPException(
                400,
                "Invalid Category"
            )

    return banner_repository.create_banner_repo(
        db,
        payload,
        image,
        token
    )

def get_banners_service(
    db: Session,
    token: dict,
    category_id: Optional[int] = None,
):
    banners = (
        banner_repository
        .get_banners_repo(
            db,
            category_id,
            token
        )
    )

    return [
        BannerResponse(
            id=item.id,
            title=item.title,
            description=item.description,
            image_url=build_image_url(
                item.image_url
            ),
            category_id=item.category_id,
            category_name=(
                item.category.name
                if item.category
                else None
            ),
            category_image_url=(
                build_image_url(
                    item.category.images[0].image_url
                )
                if item.category
                   and item.category.images
                else None
            ),
            is_active=item.is_active,
            created_at=item.created_at
        )
        for item in banners
    ]

def get_banner_by_id_service(
    db: Session,
    banner_id: int
):

    banner = (
        banner_repository
        .get_banner_by_id_repo(
            db,
            banner_id
        )
    )

    if not banner:
        raise HTTPException(
            status_code=404,
            detail="Banner not found"
        )

    return banner

def update_banner_service(
    db: Session,
    banner_id: int,
    payload: BannerUpdate,
    image: UploadFile = None
):

    update_data = {
        k: v
        for k, v in payload.model_dump(
            exclude_unset=True
        ).items()
        if v is not None
    }

    if (
        "category_id"
        in update_data
    ):

        category = (
            db.query(Category)
            .filter(
                Category.id ==
                update_data["category_id"],
                Category.is_deleted == False
            )
            .first()
        )

        if not category:
            raise HTTPException(
                status_code=400,
                detail="Invalid category"
            )

    banner = (
        banner_repository
        .update_banner_repo(
            db,
            banner_id,
            update_data,
            image
        )
    )

    if not banner:
        raise HTTPException(
            status_code=404,
            detail="Banner not found"
        )

    return banner

def delete_banner_service(
    db: Session,
    banner_id: int
):

    banner = (
        banner_repository
        .delete_banner_repo(
            db,
            banner_id
        )
    )

    if not banner:
        raise HTTPException(
            status_code=404,
            detail="Banner not found"
        )

    return banner
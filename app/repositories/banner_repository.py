from typing import Optional

from fastapi import UploadFile
from sqlalchemy.orm import Session, joinedload

from app.models.banners_model import Banner
from app.schemas.banners_schema import BannerCreate, BannerResponse
from app.utils.file_helper import delete_file, save_temp_file, move_to_final, cleanup_temp_files
from app.utils.url_helper import build_image_url


def create_banner_repo(
    db: Session,
    payload: BannerCreate,
    image: UploadFile,
    token: dict
):

    user_id = token.get("user_id")

    temp_files = []

    try:

        temp_path, filename = save_temp_file(
            image
        )

        temp_files.append(
            (temp_path, filename)
        )

        final_path = move_to_final(
            temp_path,
            filename,
            "banners"
        )

        banner = Banner(
            title=payload.title,
            description=payload.description,
            category_id=payload.category_id,
            image_url=final_path,
            created_by=user_id
        )

        db.add(banner)

        db.commit()

        db.refresh(banner)

        return banner

    except Exception as e:

        db.rollback()

        cleanup_temp_files(
            temp_files
        )

        raise e

def get_banners_repo(
    db: Session,
    token: dict,
    category_id: Optional[int] = None
):
    role = token.get("role")

    query = db.query(Banner).options(
        joinedload(Banner.category)
    )

    # ADMIN: see ALL banners (active + inactive + deleted)
    if role == "admin":
        pass  # no filters

    # NON-ADMIN: only active & not deleted
    else:
        query = query.filter(
            Banner.is_deleted == False,
            Banner.is_active == True
        )

    # category filter (applies to all roles)
    if category_id:
        query = query.filter(Banner.category_id == category_id)

    return query.order_by(Banner.id.desc()).all()

def update_banner_repo(
    db: Session,
    banner_id: int,
    update_data: dict,
    image: UploadFile = None
):

    banner = (
        db.query(Banner)
        .filter(
            Banner.id == banner_id,
            Banner.is_deleted == False
        )
        .first()
    )

    if not banner:
        return None

    temp_files = []

    try:

        for key, value in update_data.items():
            setattr(
                banner,
                key,
                value
            )

        if image:

            delete_file(
                banner.image_url
            )

            temp_path, filename = save_temp_file(
                image
            )

            temp_files.append(
                (temp_path, filename)
            )

            banner.image_url = move_to_final(
                temp_path,
                filename,
                "banners"
            )

        db.commit()

        db.refresh(
            banner
        )

        return banner

    except Exception as e:

        db.rollback()

        cleanup_temp_files(
            temp_files
        )

        raise e

def delete_banner_repo(
    db: Session,
    banner_id: int
):

    banner = (
        db.query(Banner)
        .filter(
            Banner.id == banner_id,
            Banner.is_deleted == False
        )
        .first()
    )

    if not banner:
        return None

    delete_file(
        banner.image_url
    )

    banner.is_deleted = True

    db.commit()

    return banner


def get_banner_by_id_repo(
    db: Session,
    banner_id: int
):

    banner = (
        db.query(Banner)
        .options(
            joinedload(Banner.category)
        )
        .filter(
            Banner.id == banner_id,
            Banner.is_deleted == False
        )
        .first()
    )

    if not banner:
        return None

    return BannerResponse(
        id=banner.id,
        title=banner.title,
        description=banner.description,
        image_url=build_image_url(
            banner.image_url
        ),
        category_id=banner.category_id,
        category_name=(
            banner.category.name
            if banner.category
            else None
        ),
        category_image_url=(
            build_image_url(
                banner.category.images[0].image_url
            )
            if banner.category
               and banner.category.images
            else None
        ),
        is_active=banner.is_active,
        created_at=banner.created_at
    )
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.schemas.product_schema import ProductResponse, ProductImageResponse
from app.utils.strings import ConstStrings
from app.utils.url_helper import build_image_url
from app.models.categories_model import Category
from app.repositories import category_repository
from app.schemas.category_schema import CategoryResponse, CategoryUpdate, CategoryByIdResponse, CategoryImageResponse, TopCategoryResponse


# Create category service
def create_category_service(db, payload, files, token: dict):
    existing = db.query(Category).filter(
        Category.name.ilike(payload.name)
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail=ConstStrings.CATEGORY_EXISTS
        )
    return category_repository.create_category_repo(db, payload, files, token)

# list of category service

def get_category_service(db: Session,page: int,
    limit: int,
    search: str,
    sort_by: str,
    order: str,):
    result = category_repository.get_category_repo(
        db,
        page,
        limit,
        search,
        sort_by,
        order,
    )

    result["items"] = [
        CategoryResponse(
            id=cat.id,
            name=cat.name,
            images=[
                CategoryImageResponse(
                    id=img.id,
                    image_url=build_image_url(img.image_url)
                )
                for img in cat.images
            ],
            products_count=len(cat.products),
            is_deleted=cat.is_deleted,
            deleted_by=cat.deleted_by,
            created_at=cat.created_at,
            updated_at=cat.updated_at
        )
        for cat in result["items"]
    ]

    return result
# get category by id
def get_category_by_id_service(db, category_id: int):

    category = category_repository.get_category_by_id_repo(db, category_id)

    if not category:
        raise HTTPException(
            status_code=404,
            detail=ConstStrings.NO_CATEGORY
        )
    products = sorted(
        [p for p in category.products if not p.is_deleted],
        key=lambda p: p.created_at,
        reverse=True
    )
    return CategoryByIdResponse(
        id=category.id,
        name=category.name,
        images=[
            CategoryImageResponse(
                id=img.id,
                image_url=build_image_url(img.image_url)
            )
            for img in category.images
        ],
        products_count=len([
            product
            for product in category.products
            if product.is_deleted == False
        ]),

        products=[
            ProductResponse(
                id=product.id,
                name=product.name,
                description=product.description,
                price=product.price,
                discount=product.discount,
                discount_price=product.discount_price,
                return_policy=product.return_policy,
                category_id=product.category_id,
                category_name=product.category.name,
                images=[
                    ProductImageResponse(
                        id=image.id,
                        image_url=build_image_url(image.image_url)
                    )
                    for image in product.images
                ],
                is_deleted=product.is_deleted,
                is_featured=product.is_featured,
                created_by=product.created_by,
                deleted_by=product.deleted_by,
                created_at=product.created_at,
                updated_at=product.updated_at,
            )
            for product in products
            if product.is_deleted == False
        ],
        is_deleted=category.is_deleted,
        deleted_by=category.deleted_by,
        created_at=category.created_at,
        updated_at=category.updated_at,
    )

# bulk category service
def create_category_bulk_service(db, payload,token: dict):

    category_objects = []

    for item in payload:
        existing = db.query(Category).filter(
            Category.name.ilike(item.name)
        ).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"{ConstStrings.CATEGORY_EXISTS}: {item.name}"
            )
        # Validate name
        if not item.name.strip():
            raise HTTPException(
                status_code=400,
                detail=ConstStrings.CATEGORY_NAME_EMPTY
            )

        category_objects.append(
            Category(name=item.name)
        )

    return category_repository.create_category_bulk_repo(
        db,
        category_objects,token
    )
# update category service


def update_category_service(db: Session, id: int, payload: CategoryUpdate, files, token: dict):

    #   Get existing record
    category = db.query(Category).filter(
        Category.id == id,
        Category.is_deleted == False
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail=ConstStrings.NO_CATEGORY
        )

    #  Only incoming fields
    update_data = payload.model_dump(exclude_unset=True)

    #  If nothing sent and no files
    if not update_data and not files:
        raise HTTPException(
            status_code=400,
            detail=ConstStrings.NO_UPDATE
        )

    #  Check "no changes detected" (only if no files)
    if not files:
        no_change = True
        for key, value in update_data.items():
            if getattr(category, key) != value:
                no_change = False
                break

        if no_change:
            raise HTTPException(
                status_code=400,
                detail=ConstStrings.NO_CHANGE
            )

    #  Validate duplicate name
    if "name" in update_data:
        existing = db.query(Category).filter(
            Category.name.ilike(update_data["name"]),
            Category.id != id
        ).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail=ConstStrings.CATEGORY_EXISTS
            )

    #   Update repo
    return category_repository.update_category_repo(
        db,
        category,
        update_data,
        files,
        token
    )
# Soft delete category
def delete_category_service(db, category_id: int,token: dict):

    category = db.query(Category).filter(
        Category.id == category_id,
        Category.is_deleted == False
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail=ConstStrings.NO_CATEGORY
        )

    return category_repository.delete_category_repo(db, category_id, token)

# Delete Single Category Image Service
def delete_category_image_service(
    db: Session,
    image_id: int
):
    return category_repository.delete_category_image_repo(
        db,
        image_id
    )

# Top Categories Service
def get_top_categories_service(
    db: Session,
):
    categories = category_repository.get_top_categories_repo(
        db,
     )
    total_sales = sum(
        item["total_sales"]
        for item in categories
    )
    return [
        TopCategoryResponse(
            category_id=category['category_id'],
            category_name=category['category_name'],
            total_quantity=category['total_quantity'],
            total_sales=category['total_sales'],
            sales_percentage=round(
                (
                 category["total_sales"] / total_sales * 100
                ) if total_sales > 0 else 0,
                2
            ),
            images=[
                CategoryImageResponse(
                    id=img["id"],
                    image_url=build_image_url(
                        img["image_url"]
                    )
                )
                for img in category["images"]
            ],
        )
        for category in categories
    ]
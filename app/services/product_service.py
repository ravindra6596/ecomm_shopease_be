from sqlalchemy.orm import Session

from app.services import notification_service
from app.utils.enums import NotificationType
from app.utils.strings import ConstStrings
from app.models.categories_model import Category
from app.models.products_model import Product
from app.repositories import products_repository
from app.schemas.product_schema import ProductCreate, ProductResponse, ProductImageResponse
from app.utils.url_helper import build_image_url


# Create product service
def create_product_service(db: Session, product: ProductCreate,files: list,token: dict):
    #  Validate category exists
    category = db.query(Category).filter(
        Category.id == product.category_id,
        Category.is_deleted == False
    ).first()
    # Validate name
    if not product.name.strip():
        raise HTTPException(
            status_code=400,
            detail=ConstStrings.PRODUCT_NAME_EMPTY
        )
    if not category:
        raise HTTPException(
            status_code=400,
            detail=ConstStrings.INVALID_CATEGORY
        )
    existing = db.query(Category).filter(
        Product.name.ilike(product.name)
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail=ConstStrings.PRODUCT_EXISTS
        )
        # 🔥 CALCULATION HERE
    discount_percent = product.discount or 0

    discount_price = round(product.price * (100 - discount_percent) / 100)

    create_product = products_repository.create_product_repo(db, product,files,token,discount_price)
        #     SEND NOTIFICATION HERE (business logic)
    notification_service.send_notification_to_all_users(
        db=db,
        title="New Product Added",
        body=f"'{product.name}' has been added successfully and is now available in your catalog.",
        notification_type=NotificationType.PRODUCT,
        reference_id=create_product.id
    )
    return create_product


# List of products service

def get_products_service(
        db,
        page,
        limit,
        search,
        category_id,
        min_price,
        max_price,
        sort_by,
        order,
):
    result = products_repository.get_products_repo(
        db,
        page,
        limit,
        search,
        category_id,
        min_price,
        max_price,
        sort_by,
        order,

    )
    # is_admin = token.get("role") == "admin"
    result["items"] = [
        # ProductResponse.model_validate(item)
        ProductResponse(
            id=item.id,
            name=item.name,
            description=item.description,
            price=item.price,
            discount=item.discount,
            discount_price=item.discount_price,
            return_policy=item.return_policy,
            category_id=item.category_id,
            category_name=item.category.name if item.category else None,
            images=[
                ProductImageResponse(
                    id=img.id,
                    image_url=build_image_url(img.image_url)
                )
                for img in item.images
            ],
            # ONLY FOR ADMIN
            # created_by=item.created_by if is_admin else None,
            is_deleted=item.is_deleted,
            deleted_by=item.deleted_by,
            created_at=item.created_at,
            is_featured=item.is_featured,
            updated_at=item.updated_at
        )
        for item in result["items"]
    ]

    return result


# product by id
def get_product_by_id(db, id):
    return products_repository.get_product_by_id_repo(db, id)

# update product by
def update_product_service(db, id: int, product, files, token: dict):

    # CLEAN FILES (IMPORTANT FIX)
    if files:
        files = [f for f in files if hasattr(f, "filename") and f.filename]
    else:
        files = None

    update_data = {
        k: v for k, v in product.model_dump(exclude_unset=True).items()
        if v is not None and v != ""
    }

    # Check if any fields are being updated
    if not update_data and not files:
        raise HTTPException(400, "No fields provided for update")

    if "category_id" in update_data:
        category = db.query(Category).filter(
            Category.id == update_data["category_id"],
            Category.is_deleted == False
        ).first()

        if not category:
            raise HTTPException(400, ConstStrings.INVALID_CATEGORY)

    if "price" in update_data:
        if update_data["price"] <= 0:
            raise HTTPException(400, ConstStrings.PRICE_NOT_ZERO)
        # 🔥 GET FINAL VALUES (IMPORTANT)
    product_db = db.query(Product).filter(Product.id == id).first()

    price = update_data.get("price", product_db.price)
    discount = update_data.get("discount", product_db.discount or 0)

    discount_price = round(price * (100 - discount) / 100)

    update_data["discount_price"] = discount_price

    return products_repository.update_product_repo(
        db,
        id,
        update_data,
        files,   #  cleaned files
        token
    )

from fastapi import HTTPException
# soft delete product
def soft_delete_product_service(db,  id: int,token: dict):

    product = db.query(Product).filter(
        Product.id == id,
        Product.is_deleted == False
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail=ConstStrings.NO_PRODUCT
        )

    return products_repository.soft_delete_product_repo(db, id, token)

def create_products_bulk_service(db, payload, token: dict):
    #   Fetch valid category IDs
    valid_category_ids = products_repository.get_valid_category_ids_repo(db)

    product_objects = []

    for item in payload:

        #   Invalid category check
        if item.category_id not in valid_category_ids:
            raise HTTPException(
                status_code=400,
                detail=f"{ConstStrings.INVALID_CATEGORY}: {item.category_id}"
            )

        product_objects.append(
            Product(
                name=item.name,
                description=item.description,
                price=item.price,
                category_id=item.category_id
            )
        )

    return products_repository.create_products_bulk_repo(db, product_objects,token)


# Delete Single Product Image Service
def delete_product_image_service(
    db: Session,
    image_id: int
):

    return products_repository.delete_product_image_repo(
        db,
        image_id
    )
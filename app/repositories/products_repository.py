import math
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import asc, desc, or_, cast, String, func
from sqlalchemy.orm import Session, joinedload

from app.models import ProductImage
from app.utils.file_helper import cleanup_temp_files, save_temp_file, move_to_final, delete_multiple_files, delete_file
from app.utils.strings import ConstStrings
from app.models.categories_model import Category
from app.models.products_model import Product
from app.schemas.product_schema import ProductCreate, ProductResponse, ProductImageResponse
from app.utils.url_helper import build_image_url


# Create product repo

def create_product_repo(db: Session, product: ProductCreate, files: list, token: dict,discount_price: float ):

    user_id = token.get("user_id")
    temp_files = []

    try:
        # 1️⃣ Save temp files
        for file in files:
            temp_path, filename = save_temp_file(file)
            temp_files.append((temp_path, filename))

        # 2️⃣ Create product
        product_repo = Product(
            name=product.name,
            description=product.description,
            price=product.price,
            category_id=product.category_id,
            created_by=user_id,
            discount=product.discount,
            discount_price=discount_price,
            return_policy=product.return_policy
        )

        db.add(product_repo)
        db.flush()

        # 3️⃣ Move files + attach to DB
        image_urls = []
        for temp_path, filename in temp_files:
            url = move_to_final(temp_path, filename)
            image_urls.append(url)

            db.add(ProductImage(
                product_id=product_repo.id,
                image_url=url
            ))

        # 4️⃣ Commit
        db.commit()
        db.refresh(product_repo)

        return product_repo

    except Exception as e:
        db.rollback()
        cleanup_temp_files(temp_files)
        raise e

# list of products
def get_products_repo(
    db: Session,
    page: int = 1,
    limit: int = 10,
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by=None,
    order=None,
):
    query = db.query(Product).options(
        joinedload(Product.category),
                joinedload(Product.images)
    ).filter(
        Product.is_deleted == False
    )

    # Search filter
    if search:
        search = search.strip()

        # if search.lower() in [ConstStrings.TRUE, ConstStrings.FALSE]:
        #     query = query.filter(Product.is_deleted == (search.lower() == ConstStrings.TRUE))
        # else:
        query = query.join(Category, Product.category_id == Category.id)
        query = query.filter(
                or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.description.ilike(f"%{search}%"),
                    Category.name.ilike(f"%{search}%"),  # category search
                    cast(Product.created_at, String).ilike(f"%{search}%"),
                    cast(Product.updated_at, String).ilike(f"%{search}%"),
                )
            )
    #   FILTER BY CATEGORY
    if category_id is not None:
        query = query.filter(Product.category_id == category_id)

    #  PRICE RANGE FILTER
    if min_price is not None:
        query = query.filter(Product.price >= min_price)

    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    #  COUNT (remove ORDER BY issue)
    total = query.order_by(None).count()

    #   SORTING (Enum safe)
    # sort_column = getattr(Product, sort_by.value, Product.id)
    sort_column = getattr(Product, sort_by, None)
    try:
        column_type = sort_column.property.columns[0].type
        if isinstance(column_type, String):
            sort_column = func.lower(sort_column)
    except Exception:
        pass

    if order.value == ConstStrings.ASCENDING:
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    #  PAGINATION
    total_pages = math.ceil(total / limit)
    offset = (page - 1) * limit

    items = query.offset(offset).limit(limit).all()

    # response
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "is_previous": page > 1,
        "is_next": page < total_pages,
        "items": items
    }

# get product by id
def get_product_by_id_repo(db, id):
    product = db.query(Product).options(
        joinedload(Product.category),
        joinedload(Product.images)
    ).filter(
        Product.id == id,
        Product.is_deleted == False
    ).first()
    # is_admin = token.get("role") == "admin"
    if not product:
        return None

    return ProductResponse(
    id=product.id,
    name=product.name,
    description=product.description,
    price=product.price,
    discount=product.discount,
    discount_price=product.discount_price,
    return_policy=product.return_policy,
    category_id=product.category_id,
    category_name=product.category.name if product.category else None,
    images=[
        ProductImageResponse(
            id=img.id,
            image_url=build_image_url(img.image_url)
        )
        for img in product.images
    ],
            # ONLY FOR ADMIN
    # created_by=product.created_by if is_admin else None,
    is_deleted=product.is_deleted,
    is_featured=product.is_featured,
    deleted_by=product.deleted_by,
    created_at=product.created_at,
    updated_at=product.updated_at
)


# Update product
def update_product_repo(db, id: int, update_data: dict, files, token: dict):

    product = db.query(Product).filter(
        Product.id == id,
        Product.is_deleted == False
    ).first()

    if not product:
        return None

    temp_files = []

    try:
        #   1. Update only cleaned fields
        for key, value in update_data.items():
            setattr(product, key, value)

        #   2. Append new images logic
        if files is not None:

            for file in files:
                temp_path, filename = save_temp_file(file)
                temp_files.append((temp_path, filename))

            for temp_path, filename in temp_files:
                url = move_to_final(temp_path, filename)

                db.add(ProductImage(
                    product_id=product.id,
                    image_url=url
                ))

        db.commit()
        db.refresh(product)

        # Return ProductResponse object
        is_admin = token.get("role") == "admin"
        return ProductResponse(
            id=product.id,
            name=product.name,
            description=product.description,
            price=product.price,
            discount=product.discount,
            discount_price=product.discount_price,
            return_policy=product.return_policy,
            category_id=product.category_id,
            category_name=product.category.name if product.category else None,
            images=[
                ProductImageResponse(
                    id=img.id,
                    image_url=build_image_url(img.image_url)
                )
                for img in product.images
            ],
            created_by=product.created_by if is_admin else None,
            is_deleted=product.is_deleted,
            is_featured=product.is_featured,
            deleted_by=product.deleted_by,
            created_at=product.created_at,
            updated_at=product.updated_at
        )

    except Exception as e:
        db.rollback()
        cleanup_temp_files(temp_files)
        raise e

# soft delete product
def soft_delete_product_repo(db, id: int, token: dict):

    product = db.query(Product).filter(
        Product.id == id,
        Product.is_deleted == False
    ).first()

    if not product:
        return None

    try:
        # 1. Collect image paths
        image_paths = [img.image_url for img in product.images]

        # 2. Delete files from storage
        delete_multiple_files(image_paths)

        #  3. Delete image records from DB
        for img in product.images:
            db.delete(img)

        # 4. Soft delete product
        product.is_deleted = True
        product.deleted_by = token.get(ConstStrings.USER_ID_FIELD)

        db.commit()
        db.refresh(product)

        return product

    except Exception as e:
        db.rollback()
        raise e


def create_products_bulk_repo(db: Session, products: list[Product],token: dict):
    db.add_all(products)
    db.commit()

    for p in products:
        db.refresh(p)

    return products


def get_valid_category_ids_repo(db: Session):
    return {c.id for c in db.query(Category.id).all()}

# Delete Single Product Image Repo
def delete_product_image_repo(
    db: Session,
    image_id: int
):

    image = db.query(ProductImage).filter(
        ProductImage.id == image_id
    ).first()

    if not image:
        raise HTTPException(
            status_code=404,
            detail=ConstStrings.IMAGE_NOT_FOUND
        )

    # delete physical file
    delete_file(image.image_url)

    # delete db record
    db.delete(image)

    db.commit()

    return True
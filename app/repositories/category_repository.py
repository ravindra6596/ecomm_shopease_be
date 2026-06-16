import math

from fastapi import HTTPException
from sqlalchemy import asc, desc, or_, cast, String, func
from sqlalchemy.orm import Session, joinedload

from app.models.categories_model import Category
from app.models.categories_images_model import CategoryImage
from app.models.order_items_model import OrderItem
from app.models.order_model import Order
from app.models.products_model import Product
from app.utils.file_helper import cleanup_temp_files, save_temp_file, move_to_final, delete_multiple_files, delete_file
from app.utils.strings import ConstStrings


# Create Category
def create_category_repo(db: Session, payload, files: list, token):
    user_id = token.get(ConstStrings.USER_ID_FIELD)
    temp_files = []

    try:
        # 2️⃣ Create category
        category = Category(
            name=payload.name,
            created_by=user_id
        )

        db.add(category)
        db.flush()

        # 3️⃣ Save and attach only first image (single image per category)
        if files and len(files) > 0:
            file = files[0]
            temp_path, filename = save_temp_file(file)
            temp_files.append((temp_path, filename))

            url = move_to_final(temp_path, filename, upload_dir="categories")

            db.add(CategoryImage(
                category_id=category.id,
                image_url=url
            ))

        # 4️⃣ Commit
        db.commit()
        db.refresh(category)

        return category

    except Exception as e:
        db.rollback()
        cleanup_temp_files(temp_files)
        raise e


# get all category
def get_category_repo(
        db: Session,
        page: int,
        limit: int,
        search: str,
        sort_by: str,
        order: str,
):
    query = db.query(Category).options(
        joinedload(Category.images)
    ).filter(
        Category.is_deleted == False
    )

    #  Search
    if search:
        query = query.filter(
            or_(
                Category.name.ilike(f"%{search}%"),
                cast(Category.created_at, String).ilike(f"%{search}%"),
                cast(Category.updated_at, String).ilike(f"%{search}%")
            )
        )

    #   Sorting
    # sort_column = getattr(Category, sort_by, Category.id)
    sort_column = getattr(Category, sort_by, None)
    try:
        column_type = sort_column.property.columns[0].type
        if isinstance(column_type, String):
            sort_column = func.lower(sort_column)
    except Exception:
        pass

    if order == ConstStrings.ASCENDING:
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    # Pagination
    total = query.count()
    total_pages = math.ceil(total / limit)
    offset = (page - 1) * limit

    categories = query.offset(offset).limit(limit).all()
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "is_previous": page > 1,
        "is_next": page < total_pages,
        "items": categories
    }


# get category by id
def get_category_by_id_repo(db, category_id: int):
    return db.query(Category).options(
        joinedload(Category.images)
    ).filter(
        Category.id == category_id,
        Category.is_deleted == False
    ).first()


# Insert bulk category records
def create_category_bulk_repo(db, categories, token):
    user_id = token.get(ConstStrings.USER_ID_FIELD)
    for category in categories:
        category.created_by = user_id
    db.add_all(categories)
    db.commit()

    for category in categories:
        db.refresh(category)

    return categories


# Update category
def update_category_repo(db: Session, category: Category, update_data: dict, files, token):
    temp_files = []

    try:
        # 1️⃣ Update fields
        for key, value in update_data.items():
            setattr(category, key, value)

        # 2️⃣ Handle image replacement (single image per category)
        if files is not None and len(files) > 0:
            # Delete existing images
            existing_images = db.query(CategoryImage).filter(
                CategoryImage.category_id == category.id
            ).all()

            for img in existing_images:
                delete_file(img.image_url)
                db.delete(img)

            # Save new image (only first one)
            file = files[0]
            temp_path, filename = save_temp_file(file)
            temp_files.append((temp_path, filename))

            url = move_to_final(temp_path, filename, upload_dir="categories")

            db.add(CategoryImage(
                category_id=category.id,
                image_url=url
            ))

        db.commit()
        db.refresh(category)

        return category

    except Exception as e:
        db.rollback()
        cleanup_temp_files(temp_files)
        raise e


# soft delete
def delete_category_repo(db, category_id: int, token: dict):
    category = db.query(Category).options(
        joinedload(Category.images)
    ).filter(
        Category.id == category_id,
        Category.is_deleted == False
    ).first()

    if not category:
        return None

    try:
        # 1. Collect image paths
        image_paths = [img.image_url for img in category.images]

        # 2. Delete files from storage
        delete_multiple_files(image_paths)

        # 3. Delete image records from DB
        for img in category.images:
            db.delete(img)

        # extract user_id from token
        user_id = token.get(ConstStrings.USER_ID_FIELD)

        category.is_deleted = True
        category.deleted_by = user_id
        #  soft delete all linked products (IMPORTANT)
        db.query(Product).filter(
            Product.category_id == category_id,
            Product.is_deleted == False
        ).update(
            {
                Product.is_deleted: True,
                Product.deleted_by: user_id
            },
            synchronize_session=False
        )

        db.commit()
        db.refresh(category)

        return category

    except Exception as e:
        db.rollback()
        raise e
# Top Categories Repo
def get_top_categories_repo(db: Session):

    top_categories = (
        db.query(
            Category,
            func.coalesce(
                func.sum(OrderItem.quantity),
                0
            ).label("total_quantity"),
            func.coalesce(
                func.sum(
                    OrderItem.quantity * OrderItem.price
                ),
                0
            ).label("total_sales")
        )
        .options(
            joinedload(Category.images)
        )
        .outerjoin(
            Product,
            Product.category_id == Category.id
        )
        .outerjoin(
            OrderItem,
            OrderItem.product_id == Product.id
        )
        .outerjoin(
            Order,
            Order.id == OrderItem.order_id
        )
        .filter(
            or_(
                Order.id.is_(None),
                Order.payment_status == "success"
            )
        )
        .group_by(Category.id)
        .order_by(
            desc("total_quantity")
        )
        .limit(5)
        .all()
    )

    return [
        {
            "category_id": category.id,
            "category_name": category.name,
            "total_quantity": int(total_quantity or 0),
            "total_sales": float(total_sales or 0),
            "images": [
                {
                    "id": image.id,
                    "image_url": image.image_url
                }
                for image in category.images
            ]
        }
        for category, total_quantity, total_sales in top_categories
    ]


# Delete Single Category Image Repo
def delete_category_image_repo(
    db: Session,
    image_id: int
):
    image = db.query(CategoryImage).filter(
        CategoryImage.id == image_id
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
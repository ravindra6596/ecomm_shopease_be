from typing import Optional

from sqlalchemy import desc, func
from sqlalchemy.orm import Session, joinedload

from app.models import Category
from app.models.address_model import Address
from app.models.banners_model import Banner
from app.models.cart_item_model import CartItem
from app.models.order_items_model import OrderItem
from app.models.products_model import Product
from app.models.wishlist_model import Wishlist

# Delivery Address Repo
def get_delivery_address_repo(
    db: Session,
    user_id: int
):

    return (
        db.query(Address)
        .filter(
            Address.user_id == user_id,
            Address.is_deleted == False,
            Address.is_default == True
        ).first()
    )

# Popular Products Repo
def get_popular_products_repo(
    db: Session,
    category_id: Optional[int] = None
):

    query = (
        db.query(
            Product,
            func.coalesce(
                func.sum(OrderItem.quantity),
                0
            ).label("total_sold")
        ).outerjoin(
            OrderItem,
            OrderItem.product_id == Product.id
        ).filter(
            Product.is_deleted == False
        )
    )

    if category_id:
        query = query.filter(
            Product.category_id == category_id
        )
    return (
        query.group_by(Product.id)
        .order_by(desc("total_sold"))
        .limit(6).all()
    )

# New Arrivals Repo
def get_new_arrivals_repo(
    db: Session,
    category_id: Optional[int] = None
):

    query = (
        db.query(Product)
        .filter(Product.is_deleted == False)
    )

    if category_id:
        query = query.filter(Product.category_id == category_id)

    return (
        query
        .order_by(Product.created_at.desc()).all()
    )


# Featured Products Repo
def get_featured_products_repo(
    db: Session,
    category_id: Optional[int] = None
):
    products = (
        db.query(Product)
        .options(
            joinedload(Product.images)
        ).filter(
            Product.is_deleted == False,
            Product.is_featured == True
        )
    )

    if category_id:
        products = products.filter(
            Product.category_id == category_id
        )
    return products.limit(6).all()

# Trending Products Repo
def get_trending_products_repo(
    db: Session,
    category_id: Optional[int] = None
):

    query = (
        db.query(
            Product,

            (func.count(func.distinct(Wishlist.id))
                +func.count(func.distinct(CartItem.id))
            ).label("trend_score")
        ).outerjoin(
            Wishlist,
            Wishlist.product_id
            == Product.id
        ).outerjoin(
            CartItem,
            CartItem.product_id == Product.id
        ).filter(
            Product.is_deleted == False
        )
    )

    if category_id:
        query = query.filter(
            Product.category_id == category_id
        )

    return (
        query
        .group_by(Product.id)
        .order_by(desc("trend_score"))
        .limit(6)
        .all()
    )

# Banner Repo
def get_home_banners_repo(
    db: Session,
    category_id: Optional[int] = None
):

    base_query = (
        db.query(Banner)
        .join(Category, Banner.category_id == Category.id)
        .options(joinedload(Banner.category))
        .filter(
            Banner.is_deleted == False,
            Banner.is_active == True
        )
    )

    # =========================
    # CASE 1: category selected
    # =========================
    if category_id and category_id != 0:

        return (
            base_query
            .filter(Banner.category_id == category_id)
            .order_by(Banner.id.desc())
            .all()
        )

    # =========================
    # CASE 2: homepage (1 per category)
    # =========================

    subquery = (
        db.query(
            Banner.category_id,
            func.max(Banner.id).label("max_id")
        )
        .filter(
            Banner.is_deleted == False,
            Banner.is_active == True,
            Banner.category_id.isnot(None)
        )
        .group_by(Banner.category_id)
        .subquery()
    )

    result = (
        db.query(Banner)
        .join(subquery, Banner.id == subquery.c.max_id)
        .join(Category, Banner.category_id == Category.id)
        .options(joinedload(Banner.category))
        .order_by(Category.name.asc())
        .all()
    )

    return result
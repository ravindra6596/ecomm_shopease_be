# Add Wishlist Service
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Product
from app.repositories import wishlist_repository
from app.utils.strings import ConstStrings


def add_wishlist_service(
    db: Session,
    payload,
    token
):

    product = db.query(Product).filter(
        Product.id == payload.product_id,
        Product.is_deleted == False
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail=ConstStrings.NO_PRODUCT
        )

    return wishlist_repository.add_wishlist_repo(
        db,
        payload,
        token
    )

# Get Wishlist Service
def get_wishlist_service(
    db: Session,
    token
):

    return wishlist_repository.get_wishlist_repo(
        db,
        token
    )

# Remove Wishlist Service
def remove_wishlist_service(
    db: Session,
    wishlist_id: int,
    token
):

    return wishlist_repository.remove_wishlist_repo(
        db,
        wishlist_id,
        token
    )

# Clear Wishlist Service
def clear_wishlist_service(
    db: Session,
    token
):

    return wishlist_repository.clear_wishlist_repo(
        db,
        token
    )
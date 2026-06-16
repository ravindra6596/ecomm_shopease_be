# Add Wishlist Repo
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.wishlist_model import Wishlist
from app.utils.strings import ConstStrings


def add_wishlist_repo(
    db: Session,
    payload,
    token
):

    user_id = token.get(
        ConstStrings.USER_ID_FIELD
    )

    existing = db.query(Wishlist).filter(
        Wishlist.user_id == user_id,
        Wishlist.product_id == payload.product_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail=ConstStrings.ALREADY_IN_WISHLIST
        )

    wishlist = Wishlist(
        user_id=user_id,
        product_id=payload.product_id
    )

    db.add(wishlist)
    db.commit()
    db.refresh(wishlist)

    return wishlist

# Get Wishlist Repo
def get_wishlist_repo(
    db: Session,
    token
):

    user_id = token.get(
        ConstStrings.USER_ID_FIELD
    )

    role = token.get("role")

    query = db.query(Wishlist)

    if role == "user":
        query = query.filter(
            Wishlist.user_id == user_id
        )

    return query.order_by(
        Wishlist.id.desc()
    ).all()

# Remove Wishlist Repo
def remove_wishlist_repo(
    db: Session,
    wishlist_id: int,
    token
):

    user_id = token.get(
        ConstStrings.USER_ID_FIELD
    )

    role = token.get("role")

    query = db.query(Wishlist).filter(
        Wishlist.id == wishlist_id
    )

    if role == "user":
        query = query.filter(
            Wishlist.user_id == user_id
        )

    wishlist = query.first()

    if not wishlist:
        raise HTTPException(
            status_code=404,
            detail=ConstStrings.WISHLIST_NOT_FOUND
        )

    db.delete(wishlist)
    db.commit()

    return True

# Clear Wishlist Repo
def clear_wishlist_repo(
    db: Session,
    token
):

    user_id = token.get(
        ConstStrings.USER_ID_FIELD
    )

    role = token.get("role")

    query = db.query(Wishlist)

    # normal user -> own wishlist only
    if role == "user":
        query = query.filter(
            Wishlist.user_id == user_id
        )

    query.delete(
        synchronize_session=False
    )

    db.commit()

    return True
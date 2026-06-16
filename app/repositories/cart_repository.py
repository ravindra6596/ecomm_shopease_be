# Add To Cart Repo
import math

from fastapi import HTTPException
from sqlalchemy import asc, String, func, or_, cast, desc
from sqlalchemy.orm import Session

from app.models import Product
from app.models.cart_item_model import CartItem
from app.models.cart_model import Cart
from app.models.user_model import User
from app.utils.cart_filter import get_cart_filter
from app.utils.strings import ConstStrings

# Add To Cart Repo
def add_to_cart_repo(db: Session, payload, token):
    user_id = token.get(ConstStrings.USER_ID_FIELD)

    # check cart exists
    cart = db.query(Cart).filter(
        Cart.user_id == user_id
    ).first()

    # create cart if not exists
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.flush()

    # check product already exists in cart
    existing_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == payload.product_id
    ).first()
    if existing_item:
        raise HTTPException(
            status_code=400,
            detail=ConstStrings.ALREADY_IN_CART
        )
    # increase quantity
    if existing_item:
        existing_item.quantity += payload.quantity
    else:
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=payload.product_id,
            quantity=1
        )
        db.add(cart_item)

    db.commit()
    db.refresh(cart)

    return cart
 

def add_to_cart_repo_new(
    db: Session,
    payload,
    user_id=None,
    guest_id=None
):

    # FIND CART
    if user_id:

        cart = db.query(Cart).filter(
            Cart.user_id == user_id
        ).first()

    else:

        cart = db.query(Cart).filter(
            Cart.guest_id == guest_id
        ).first()

    # CREATE CART
    if not cart:

        cart = Cart(
            user_id=user_id,
            guest_id=guest_id
        )

        db.add(cart)
        db.flush()

    # FIND EXISTING ITEM
    existing_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == payload.product_id
    ).first()

    # INCREASE QUANTITY
    if existing_item:

        raise HTTPException(
            status_code=400,
            detail=ConstStrings.ALREADY_IN_CART
        )

    else:

        cart_item = CartItem(
            cart_id=cart.id,
            product_id=payload.product_id,
            # quantity=payload.quantity
        )

        db.add(cart_item)

    db.commit()
    db.refresh(cart)

    return cart
# Get Cart Items Repo
def get_cart_items_repo(db: Session, token: dict):

    user_id = token.get(ConstStrings.USER_ID_FIELD)
    role = token.get("role")

    # # admin -> all carts
    # if role == "admin":
    #     cart_items = db.query(CartItem).all()
    #
    # # user -> own cart only
    # else:
    #     cart_items = (
    #         db.query(CartItem).join(Cart).filter(Cart.user_id == user_id).all()
    #     )
    cart_items = (
        db.query(CartItem)
        .join(Cart)
        .filter(Cart.user_id == user_id)
        .all()
    )
    return cart_items

# Get Cart By id Repo
def get_cart_by_id_repo(db, cart_id: int,token:dict):
    return db.query(Cart).filter(
        Cart.id == cart_id,
    ).first()

# Update Cart Quantity Repo
def update_cart_quantity_repo(
    db: Session,
    cart_item_id: int,
    payload,
    token
):

    user_id = token.get(ConstStrings.USER_ID_FIELD)
    role = token.get("role")

    query = (
        db.query(CartItem)
        .join(Cart)
        .filter(CartItem.id == cart_item_id)
    )

    # user -> own cart only
    if role == "user":
        query = query.filter(
            Cart.user_id == user_id
        )

    cart_item = query.first()

    if not cart_item:
        raise HTTPException(
            status_code=404,
            detail=ConstStrings.CART_NOT_FOUND
        )

    # update quantity
    cart_item.quantity = payload.quantity

    db.commit()
    db.refresh(cart_item)

    return cart_item

# Remove Cart Item Repo
def remove_cart_item_repo(
    db: Session,
    id: int,
    token
):

    user_id = token.get(ConstStrings.USER_ID_FIELD)
    role = token.get("role")

    query = (
        db.query(CartItem)
        .join(Cart)
        .filter(CartItem.id == id)
    )

    # normal user -> own cart only
    if role == "user":
        query = query.filter(
            Cart.user_id == user_id
        )

    cart_item = query.first()

    if not cart_item:
        raise HTTPException(
            status_code=404,
            detail=ConstStrings.CART_NOT_FOUND
        )

    db.delete(cart_item)
    db.commit()

    return True

# Clear Cart Repo
def clear_cart_repo(
    db: Session,
    token
):

    user_id = token.get(ConstStrings.USER_ID_FIELD)
    role = token.get("role")

    # admin -> clear all carts
    if role == "admin":

        db.query(CartItem).delete(
            synchronize_session=False
        )

    # normal user -> clear own cart
    else:

        cart = db.query(Cart).filter(
            Cart.user_id == user_id
        ).first()

        if not cart:
            raise HTTPException(
                status_code=404,
                detail=ConstStrings.CART_NOT_FOUND
            )

        db.query(CartItem).filter(
            CartItem.cart_id == cart.id
        ).delete(
            synchronize_session=False
        )

    db.commit()

    return True

# Get All Admin Carts
def get_all_admin_carts_repo(
        db: Session,
        page: int,
        limit: int,
        search: str,
        sort_by: str,
        order: str,
):

    query = (
        db.query(Cart)
        .join(User)
        .outerjoin(CartItem)
        .outerjoin(Product)
    )

    # Search
    if search:
        query = query.filter(
            or_(
                User.name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                cast(Cart.id, String).ilike(f"%{search}%")
            )
        )

    # Group by cart
    query = query.group_by(
        Cart.id,
        User.id
    )

    # Sorting
    if sort_by == "user_name":

        sort_column = User.name

    elif sort_by == "user_email":

        sort_column = User.email

    elif sort_by == "total_items":

        sort_column = func.sum(
            CartItem.quantity
        )

    elif sort_by == "grand_total":

        sort_column = func.sum(
            CartItem.quantity * Product.price
        )

    else:

        sort_column = getattr(
            Cart,
            sort_by,
            Cart.id
        )

    # lowercase sorting for string
    try:
        column_type = sort_column.property.columns[0].type

        if isinstance(column_type, String):
            sort_column = func.lower(sort_column)

    except Exception:
        pass

    # Apply sorting
    if order == ConstStrings.ASCENDING:
        query = query.order_by(
            asc(sort_column)
        )
    else:
        query = query.order_by(
            desc(sort_column)
        )

    # Pagination
    total = query.count()

    total_pages = math.ceil(
        total / limit
    )

    offset = (page - 1) * limit

    carts = query.offset(offset).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "is_previous": page > 1,
        "is_next": page < total_pages,
        "items": carts
    }


############ NEW CART ############
def get_cart_items_repo_new(db, token, guest_id):

    filters = get_cart_filter(token, guest_id)

    query = db.query(CartItem).join(Cart)

    if "user_id" in filters:
        query = query.filter(Cart.user_id == filters["user_id"])

    elif "guest_id" in filters:
        query = query.filter(Cart.guest_id == filters["guest_id"])

    return query.all()


def update_cart_quantity_repo_new(
    db: Session,
    cart_item_id: int,
    payload,
    token: dict,
    guest_id: str
):

    filters = get_cart_filter(token, guest_id)

    query = db.query(CartItem).join(Cart).filter(
        CartItem.id == cart_item_id
    )

    if filters.get("user_id"):
        query = query.filter(Cart.user_id == filters["user_id"])
    else:
        query = query.filter(Cart.guest_id == filters["guest_id"])

    cart_item = query.first()

    if not cart_item:
        raise HTTPException(404, "Cart not found")

    cart_item.quantity = payload.quantity

    db.commit()
    db.refresh(cart_item)

    return cart_item


def remove_cart_item_repo_new(
    db: Session,
    id: int,
    token: dict,
    guest_id: str
):

    filters = get_cart_filter(token, guest_id)

    query = db.query(CartItem).join(Cart).filter(
        CartItem.id == id
    )

    if filters.get("user_id"):
        query = query.filter(Cart.user_id == filters["user_id"])
    else:
        query = query.filter(Cart.guest_id == filters["guest_id"])

    item = query.first()

    if not item:
        raise HTTPException(404, "Not found")

    db.delete(item)
    db.commit()

    return True

def clear_cart_repo_new(
    db: Session,
    token: dict,
    guest_id: str
):

    user_id = token.get(ConstStrings.USER_ID_FIELD)

    query = db.query(CartItem).join(Cart)

    # LOGGED IN USER
    if user_id:
        query = query.filter(Cart.user_id == user_id)

    # GUEST USER
    else:
        query = query.filter(Cart.guest_id == guest_id)

    deleted = query.delete(synchronize_session=False)
    db.commit()

    return deleted
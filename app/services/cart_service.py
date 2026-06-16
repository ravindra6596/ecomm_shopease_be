# Add To Cart Service
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Product
from app.repositories import cart_repository
from app.schemas.cart_schema import CartResponse, AdminCartResponse
from app.utils.strings import ConstStrings


def add_to_cart_service(db: Session, payload, token: dict):

    # validate product exists
    product = db.query(Product).filter(
        Product.id == payload.product_id,
        Product.is_deleted == False
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail=ConstStrings.NO_PRODUCT
        )

    return cart_repository.add_to_cart_repo(
        db,
        payload,
        token
    )
def add_to_cart_service_new(
    db: Session,
    payload,
    user_id=None,
    guest_id=None
):

    # VALIDATE PRODUCT
    product = db.query(Product).filter(
        Product.id == payload.product_id,
        Product.is_deleted == False
    ).first()

    if not product:

        raise HTTPException(
            status_code=404,
            detail=ConstStrings.NO_PRODUCT
        )

    return cart_repository.add_to_cart_repo(
        db=db,
        payload=payload,
        user_id=user_id,
        guest_id=guest_id
    )
# Get Cart Items Service
def get_cart_items_service(db: Session, token: dict):

    cart_items = cart_repository.get_cart_items_repo(
        db,
        token
    )

    return cart_items

# Get Cart By id Service
def get_cart_by_id_service(
    db,
    cart_id: int,
    token
):

    cart = cart_repository.get_cart_by_id_repo(
        db,
        cart_id,
        token
    )

    if not cart:
        raise HTTPException(
            status_code=404,
            detail=ConstStrings.CART_EMPTY
        )

    cart_items = cart.items

    total_items = sum(
        item.quantity
        for item in cart_items
    )

    grand_total = sum(
        item.product.price * item.quantity
        for item in cart_items
    )

    return {
        "id": cart.id,
        "user_id": cart.user_id,
        "total_items": total_items,
        "grand_total": grand_total,
        "items": [
            {
                "id": item.id,
                "product_id": item.product.id,
                "product_name": item.product.name,
                "product_price": item.product.price,
                "quantity": item.quantity,
                "total_price": item.product.price * item.quantity,
            }
            for item in cart_items
        ]
    }
# Update Cart Quantity Service
def update_cart_quantity_service(
    db: Session,
    cart_item_id: int,
    payload,
    token
):

    return cart_repository.update_cart_quantity_repo(
        db,
        cart_item_id,
        payload,
        token
    )

# Remove Cart Item Service
def remove_cart_item_service(
    db: Session,
    id: int,
    token
):

    return cart_repository.remove_cart_item_repo(
        db,
        id,
        token
    )

# Clear Cart Service
def clear_cart_service(
    db: Session,
    token
):

    return cart_repository.clear_cart_repo(
        db,
        token
    )

# Get All Admin Carts Service
def get_all_admin_carts_service(
        db: Session,
        page: int,
        limit: int,
        search: str,
        sort_by: str,
        order: str,
):
    result = cart_repository.get_all_admin_carts_repo(
        db,
        page,
        limit,
        search,
        sort_by,
        order,
    )

    result["items"] = [
        AdminCartResponse(
            id=cart.id,
            user_id=cart.user_id,
            user_name=cart.user.name if cart.user else None,
            user_email=cart.user.email if cart.user else None,

            total_items=sum(
                item.quantity
                for item in cart.items
            ),

            grand_total=sum(
                item.product.price * item.quantity
                for item in cart.items
            ),

            created_at=cart.created_at,
            updated_at=cart.updated_at,
        ).model_dump()

        for cart in result["items"]
    ]

    return result

################# NEW CART ####################
def get_cart_items_service_new(db: Session, token: dict, guest_id: str):

    return cart_repository.get_cart_items_repo_new(
        db,
        token,
        guest_id
    )

def update_cart_quantity_service_new(
    db,
    cart_item_id,
    payload,
    token,
    guest_id
):

    return cart_repository.update_cart_quantity_repo_new(
        db,
        cart_item_id,
        payload,
        token,
        guest_id
    )

def remove_cart_item_service_new(db, id, token, guest_id):

    return cart_repository.remove_cart_item_repo_new(
        db,
        id,
        token,
        guest_id
    )

def clear_cart_service_new(
    db: Session,
    token: dict,
    guest_id: str
):

    return cart_repository.clear_cart_repo_new(
        db,
        token,
        guest_id
    )
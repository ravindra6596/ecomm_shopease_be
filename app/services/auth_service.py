from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.config.config import settings
from app.email_template.email_verification_template import EMAIL_VERIFY_TEMPLATE
from app.models.cart_item_model import CartItem
from app.models.cart_model import Cart
from app.models.token import BlacklistedToken
from app.repositories import auth_repository
from app.schemas.auth_schema import UserCreate
from app.utils.auth_dependency import verify_refresh_token
from app.utils.auth_utils import hash_password, create_access_token, verify_password, create_refresh_token, \
    generate_email_verification_token
from app.utils.email import send_email
from app.utils.strings import ConstStrings

BASE_URL = settings.BASE_URL


def register_service(
    db: Session,
    emp: UserCreate
):
    existing_user = (
        auth_repository.get_user_by_email_repo(
            db,
            emp.email
        )
    )

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail=ConstStrings.USER_EXISTS
        )

    hashed_password = hash_password(emp.password)

    verification_token = generate_email_verification_token()
    user = auth_repository.register_repo(
        db,
        emp,
        hashed_password,
        verification_token
    )
    # Send email after register
    verification_link = (
        f"{BASE_URL}/auth/verify-email?"
        f"token={verification_token}"
    )

    subject = "Verify your email"

    body = EMAIL_VERIFY_TEMPLATE.format(
        name=emp.name,
        verification_link=verification_link
    )

    send_email(
        emp.email,
        subject,
        body
    )

    return user


# email verification service
def verify_email_service(
    db: Session,
    token: str
):
    user = auth_repository.get_user_by_verification_token_repo(
        db,
        token
    )

    if not user:
        return "invalid"
    if user.is_email_verified:
        return "already_verified"

    user.is_email_verified = True
    user.email_verification_token = None

    db.commit()

    return "verified"


#login
def login_service(
    db: Session,
    email: str,
    password: str,
    guest_id: str = None,
    fcm_token: str = None
):
    user = (
        auth_repository.get_user_by_email_repo(db, email)
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail=ConstStrings.NO_USER
        )
    if not user.is_email_verified:
        raise HTTPException(
            status_code=403,
            detail="Please verify your email first"
        )
    if not verify_password(
        password,
        user.password
    ):
        raise HTTPException(
            status_code=401,
            detail=ConstStrings.INVALID_PASSWORD
        )
        # optional active check
    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail=ConstStrings.ACCOUNT_INACTIVE
        )

    if fcm_token:
        user.fcm_token = fcm_token
        db.commit()
        db.refresh(user)

        # MERGE GUEST CART
    if guest_id:
        merge_guest_cart_service(
            db=db,
            user_id=user.id,
            guest_id=guest_id
        )

    token_data = {
        "name": user.name,
        "email": user.email,
        "user_id": user.id,
        "role":user.role
    }

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "is_active": user.is_active,
            "role":user.role,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }
    }

# refresh token
def refresh_access_token(refresh_token: str):
    payload = verify_refresh_token(refresh_token)
    return payload

# logout
def logout_service(db, token: str):
    blacklisted = BlacklistedToken(token=token)

    db.add(blacklisted)
    db.commit()

    return True

# Merge Guest Cart
def merge_guest_cart_service(
    db: Session,
    user_id: int,
    guest_id: str
):

    guest_cart = db.query(Cart).filter(
        Cart.guest_id == guest_id
    ).first()

    if not guest_cart:
        return

    user_cart = db.query(Cart).filter(
        Cart.user_id == user_id
    ).first()

    if not user_cart:

        guest_cart.user_id = user_id
        guest_cart.guest_id = None

        db.commit()

        return

    # MERGE ITEMS
    for guest_item in guest_cart.items:

        existing_item = db.query(CartItem).filter(
            CartItem.cart_id == user_cart.id,
            CartItem.product_id == guest_item.product_id
        ).first()

        if existing_item:

            existing_item.quantity += guest_item.quantity

        else:

            new_item = CartItem(
                cart_id=user_cart.id,
                product_id=guest_item.product_id,
                quantity=guest_item.quantity
            )

            db.add(new_item)

    db.delete(guest_cart)

    db.commit()
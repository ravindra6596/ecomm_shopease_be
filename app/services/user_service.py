from app.repositories import user_repository
from app.schemas.address_schema import AddressResponse
from app.schemas.auth_schema import UserResponse, UserDetailsResponse
from app.schemas.order_schema import OrderResponse, OrderItemResponse


# List of users
def get_users_service(
    db,
    page: int,
    limit: int,
    search: str,
    search_filter: str,
    sort_by: str,
    order: str,
    token_data: dict
):
    result = user_repository.get_users_repo(
        db,
        page,
        limit,
        search,
        search_filter,
        sort_by,
        order,
        token_data
    )

    result["users"] = [
        UserResponse.model_validate(user)
        for user in result["users"]
    ]

    return result
# get my profile using token only
def get_profile_service(db,token: dict):
    return user_repository.get_profile_repo(db, token)

# user by id
# user by id
def get_user_by_id(
    db,
    user_id,
    token: dict
):

    user = user_repository.get_user_by_id_repo(
        db,
        user_id,
        token
    )

    if not user:
        return None

    return UserDetailsResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        is_active=user.is_active,
        role=user.role,

        addresses=[
            AddressResponse.model_validate(address)
            for address in user.addresses
        ],

        orders=[
            OrderResponse(
                id=order.id,
                user_id=order.user_id,
                user_name=order.user.name if order.user else None,
                address_id=order.address_id,
                total_amount=order.total_amount,
                status=order.status,
                payment_status=order.payment_status,
                payment_method=order.payment_method,
                created_at=order.created_at,
                items=[
                    OrderItemResponse(
                        product_id=item.product_id,
                        product_name=item.product.name if item.product else None,
                        quantity=item.quantity,
                        price=item.price,
                        total_price=item.quantity * item.price,
                        discount_price=item.product.discount_price,
                        discount=item.product.discount,
                    )
                    for item in order.items
                ],
                address=order.address
            )
            for order in user.order
        ],

        created_at=user.created_at,
        updated_at=user.updated_at,
    )
# User by email
def get_user_by_email(db, email):
    return user_repository.get_user_by_email_repo(db, email)

# Update user
def update_user_service(
    db,
    user,
    token: dict
):
    return user_repository.update_user_repo(db, user,token)


# Delete user
def delete_user_service(db, user_id,token):
    return user_repository.delete_user_repo(
        db,
        user_id,token
    )
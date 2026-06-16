import math

from sqlalchemy import asc, desc, String, cast, or_, func
from sqlalchemy.orm import Session

from app.models.user_model import User
from app.utils.enums import SearchField
from app.utils.strings import ConstStrings


# Get user by email
def get_user_by_email_repo(
    db: Session,
    email: str
):
    return db.query(User).filter(
        User.email == email # need to pass whole email address for find
        # User.email.ilike(f"%{email}%") # if just want to pass some letters of email
    ).first()

def get_profile_repo(db: Session, token: dict):
    return db.query(User).filter(User.id == token[ConstStrings.USER_ID_FIELD]).first()
# List of users

def get_users_repo(
    db: Session,
    page: int,
    limit: int,
    search: str,
    search_filter: str,
    sort_by: str,
    order: str,
    token_data: dict
):
    query = db.query(User)

    # search + filter
    if search:
        column = None

        if search_filter:
            column = getattr(User, search_filter.value, None)

        #  Column-specific search
        if column is not None:
            if isinstance(column.type, String):
                query = query.filter(column.ilike(f"%{search}%"))
            else:
                # validate numeric input
                try:
                    query = query.filter(column == int(search))
                except ValueError:
                    # invalid input → fallback to global search
                    column = None

        # Global search fallback
        if column is None:
            conditions = []

            for field in SearchField:
                col = getattr(User, field.value, None)

                if col is None:
                    continue

                if isinstance(col.type, String):
                    conditions.append(col.ilike(f"%{search}%"))
                else:
                    conditions.append(cast(col, String).ilike(f"%{search}%"))

            if conditions:
                query = query.filter(or_(*conditions))

    # sorting
    sort_column = getattr(
        User,
        sort_by,
        User.id
    )

    if order.lower() == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    # pagination
    offset = (page - 1) * limit

    total = query.count()

    users = query.offset(offset).limit(limit).all()
    total_pages = math.ceil(total / limit)

    return {
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages
        },
        "users": users
    }
# User by id
def get_user_by_id_repo(db: Session, user_id: int,token: dict):
    return db.query(User).filter(
        User.id == user_id
    ).first()

# Update User
def update_user_repo(
    db,
    user_data,
    token,
):
    user_id = token.get(ConstStrings.USER_ID_FIELD )
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        return None

    update_data = user_data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(user, key, value)
    user.updated_at = func.now()
    db.commit()
    db.refresh(user)

    return user

# Delete user
def delete_user_repo(db: Session, user_id: int,token):
    user = get_user_by_id_repo(db, user_id)

    if not user:
        return None

    db.delete(user)
    db.commit()

    return user
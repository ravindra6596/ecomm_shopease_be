from sqlalchemy.orm import Session

from app.models.user_model import User
from app.schemas.auth_schema import UserCreate


def get_user_by_email_repo(
    db: Session,
    email: str
):
    return db.query(User).filter(
        User.email == email
    ).first()


def register_repo(
    db: Session,
    user: UserCreate,
    hashed_password: str,
    verification_token: str
):
    db_employee = User(
        name=user.name,
        email=user.email,
        password=hashed_password,
        email_verification_token=verification_token
    )

    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)

    return db_employee

# Email Verification
def get_user_by_verification_token_repo(
    db: Session,
    token: str
):
    return db.query(User).filter(
        User.email_verification_token == token
    ).first()
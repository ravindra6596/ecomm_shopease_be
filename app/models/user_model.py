from sqlalchemy import Column, Integer, String, DateTime, func, Boolean, Text
from sqlalchemy.orm import relationship

from app.database.connection import Base
from app.utils.strings import ConstStrings


class User(Base):
    __tablename__ = ConstStrings.USER_TABLE

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    role = Column(String(20), default=ConstStrings.USER_TABLE, nullable=False)
    is_email_verified = Column(
        Boolean,
        default=False,
        nullable=False
    )

    email_verification_token = Column(
        String(255),
        nullable=True
    )
    fcm_token = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    carts = relationship(
        "Cart",
        back_populates="user"
    )
    order = relationship(
        "Order",
        back_populates="user"
    )
    addresses = relationship(
        "Address",
        back_populates="user"
    )
    notifications = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan"
    )
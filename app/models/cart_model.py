from sqlalchemy import Column, Integer, ForeignKey, DateTime, func, String
from sqlalchemy.orm import relationship

from app.database.connection import Base
from app.utils.strings import ConstStrings


class Cart(Base):
    __tablename__ = ConstStrings.CART_TABLE

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    guest_id = Column(String,nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    items = relationship(
        "CartItem",
        back_populates="cart",
        cascade="all, delete-orphan"
    )
    user = relationship(
        "User",
        back_populates="carts"
    )
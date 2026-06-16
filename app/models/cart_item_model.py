from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.database.connection import Base
from app.utils.strings import ConstStrings


class CartItem(Base):
    __tablename__ = ConstStrings.CART_ITEMS_TABLE

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("cart.id", ondelete="CASCADE"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False, default=1)
    cart = relationship("Cart", back_populates="items")
    product = relationship("Product")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)
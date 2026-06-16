from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime, func
from sqlalchemy.orm import relationship

from app.database.connection import Base
from app.utils.strings import ConstStrings


class OrderItem(Base):
    __tablename__ = ConstStrings.ORDER_ITEMS_TABLE

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE")
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id")
    )

    quantity = Column(
        Integer,
        nullable=False
    )

    price = Column(
        Float,
        nullable=False
    )

    order = relationship(
        "Order",
        back_populates="items"
    )

    product = relationship("Product")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
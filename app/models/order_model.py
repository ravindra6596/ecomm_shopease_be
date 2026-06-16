from datetime import timedelta, datetime, timezone

from sqlalchemy import Column, Integer, ForeignKey, Float, String, DateTime, func
from sqlalchemy.orm import relationship

from app.database.connection import Base
from app.utils.enums import OrderStatus, PaymentStatus, PaymentMethod
from app.utils.strings import ConstStrings

class Order(Base):
    __tablename__ = ConstStrings.ORDERS_TABLE

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("user.id")
    )

    address_id = Column(
        Integer,
        ForeignKey("addresses.id")
    )

    total_amount = Column(
        Float,
        nullable=False,
        default=0
    )

    status = Column(
        String,
        default=OrderStatus.pending.value
    )

    payment_status = Column(
        String,
        default=PaymentStatus.pending.value
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    delivery_date = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc) + timedelta(days=5)
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete"
    )

    address = relationship("Address")
    user = relationship(
        "User",
        back_populates="order"
    )
    payment_method = Column(
        String,
        default=PaymentMethod.cod.value
    )
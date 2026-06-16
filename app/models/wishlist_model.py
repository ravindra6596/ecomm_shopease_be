from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.database.connection import Base
from app.utils.strings import ConstStrings


class Wishlist(Base):
    __tablename__ = ConstStrings.WISHLIST_ITEMS_TABLE

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("user.id")
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id")
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    product = relationship("Product")
from sqlalchemy import Column, String, Integer, Float, ForeignKey, Boolean, DateTime, func
from sqlalchemy.orm import relationship

from app.utils.strings import ConstStrings
from app.database.connection import Base

class Product(Base):
    __tablename__ = ConstStrings.PRODUCTS_TABLE

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    discount = Column(Float, nullable=True)
    discount_price = Column(Float, nullable=True)
    return_policy = Column(String, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("Category", back_populates="products") # for category name
    images = relationship("ProductImage", back_populates="product", cascade="all, delete")
    is_deleted = Column(Boolean, default=False)
    created_by = Column(Integer, nullable=True)
    deleted_by = Column(Integer, nullable=True)
    is_featured = Column(Boolean,default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)
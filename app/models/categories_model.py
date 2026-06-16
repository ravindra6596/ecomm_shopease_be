from sqlalchemy import Column, String, Integer, Boolean, DateTime, func
from sqlalchemy.orm import relationship

from app.database.connection import Base
from app.utils.strings import ConstStrings


class Category(Base):
    __tablename__ = ConstStrings.CATEGORIES_TABLE

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String, nullable=False,unique=True)
    is_deleted = Column(Boolean, default=False)
    created_by = Column(Integer, nullable=True)
    deleted_by = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    products = relationship('Product', back_populates="category")
    images = relationship("CategoryImage", back_populates="category", cascade="all, delete")

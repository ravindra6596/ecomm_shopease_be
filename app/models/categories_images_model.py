from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.connection import Base
from app.utils.strings import ConstStrings


class CategoryImage(Base):
    __tablename__ = ConstStrings.CATEGORIES_IMAGES_TABLE

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"))
    image_url = Column(String, nullable=False)
    category = relationship('Category', back_populates="images")

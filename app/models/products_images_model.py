from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.connection import Base
from app.utils.strings import ConstStrings


class ProductImage(Base):
    __tablename__ = ConstStrings.PRODUCTS_IMAGES_TABLE

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    image_url = Column(String, nullable=False)
    product = relationship('Product', back_populates="images")
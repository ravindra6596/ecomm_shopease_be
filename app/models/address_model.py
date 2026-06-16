from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base
from app.utils.strings import ConstStrings


class Address(Base):
    __tablename__ = ConstStrings.ADDRESS_TABLE

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("user.id")
    )
    full_name = Column(String)
    phone = Column(String)
    address_line = Column(String)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    pincode = Column(String)
    address_type = Column(String)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True),
    is_deleted = Column(Boolean, default=False)
    user = relationship(
        "User",
        back_populates="addresses"
    )
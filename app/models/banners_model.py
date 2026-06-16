from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, DateTime, func
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Banner(Base):
    __tablename__ = "banners"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(
        String,
        nullable=False
    )

    description = Column(
        String,
        nullable=True
    )

    image_url = Column(
        String,
        nullable=False
    )

    category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=True
    )

    category = relationship("Category")

    is_active = Column(
        Boolean,
        default=True
    )

    created_by = Column(
        Integer,
        nullable=True
    )

    is_deleted = Column(
        Boolean,
        default=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now()
    )
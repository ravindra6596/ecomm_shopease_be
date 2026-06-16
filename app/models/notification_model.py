from sqlalchemy import *
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.connection import Base
from app.utils.enums import NotificationType
from app.utils.strings import ConstStrings


class Notification(Base):
    __tablename__ = ConstStrings.NOTIFICATIONS_TABLE

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("user.id")
    )
    reference_id = Column(
        Integer,
        nullable=True
    )
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    notification_type = Column(
        Enum(NotificationType),
        nullable=False
    )
    is_read = Column(
        Boolean,
        default=False
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    user = relationship(
        "User",
        back_populates="notifications"
    )
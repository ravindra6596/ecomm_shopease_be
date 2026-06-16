from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime, Text

from app.database.connection import Base


class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"

    id = Column(Integer, primary_key=True)
    token = Column(Text, unique=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
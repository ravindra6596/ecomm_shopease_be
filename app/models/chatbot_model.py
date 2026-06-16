from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, String, JSON
from sqlalchemy.sql import func

from app.database.connection import Base


class ChatMessage(Base):

    __tablename__ = "chat_messages"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    conversation_id = Column(
        Integer,
        ForeignKey("chat_conversations.id"),
        nullable=False
    )

    sender = Column(
        String,
        nullable=False
    )
    # user / bot

    message = Column(
        Text,
        nullable=False
    )
    products = Column(JSON, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

class ChatConversation(Base):

    __tablename__ = "chat_conversations"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("user.id"),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
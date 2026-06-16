from datetime import datetime

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    userMessage: str
    botMessage: str
    createdAt: datetime
class ChatMessageResponse(BaseModel):

    id: int
    sender: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True

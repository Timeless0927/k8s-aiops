from typing import List, Optional
from pydantic import BaseModel, Field

class Message(BaseModel):
    role: str = Field(..., description="Role: user, assistant, system")
    content: str = Field(..., description="Message content")

class ChatRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = None
    temperature: float = 0.7

class ChatResponse(BaseModel):
    response: str
    usage: dict = {}

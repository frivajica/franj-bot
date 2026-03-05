from typing import List, Optional

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str = Field(pattern="^(user|assistant|system)$")
    content: str


class ChatRequest(BaseModel):
    messages: List[Message] = Field(min_length=1)
    language: Optional[str] = Field(default="en", pattern="^(en|es)$")

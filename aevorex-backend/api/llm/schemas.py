from pydantic import BaseModel, Field
from typing import Literal, List, Optional, Dict

class Message(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = Field(None, description="Alias vagy teljes model ID")

class ChatResponse(BaseModel):
    content: str
    usage: Optional[Dict] = None

class ModelsResponse(BaseModel):
    models: Dict[str, str]
    default: str

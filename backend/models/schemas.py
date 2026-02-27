from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class Role(str, Enum):
    user = "user"
    assistant = "assistant"
    system = "system"


class Message(BaseModel):
    role: Role
    content: str
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    message: str = Field(..., description="User message")
    use_search: bool = Field(default=True, description="Allow agent to search the web")
    stream: bool = Field(default=False, description="Stream response tokens")


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    sources: Optional[List[str]] = None
    tool_calls: Optional[List[str]] = None


class UploadResponse(BaseModel):
    session_id: str
    file_name: str
    message: str
    summary: str


class HistoryResponse(BaseModel):
    session_id: str
    messages: List[Message]
    total: int


class HealthResponse(BaseModel):
    status: str
    model: str
    version: str = "1.0.0"

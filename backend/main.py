"""
Kimi Agent — FastAPI entry point
"""

import os
import uuid
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from models.schemas import (
    ChatRequest,
    ChatResponse,
    UploadResponse,
    HistoryResponse,
    HealthResponse,
    Message,
)
from agent.kimi_agent import KimiAgent
from agent.memory.conversation_memory import MemoryManager

load_dotenv()

# --------------------------------------------------------------------------- #
#  App lifecycle                                                                #
# --------------------------------------------------------------------------- #

agent: KimiAgent


@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent
    agent = KimiAgent()
    yield


app = FastAPI(
    title="Kimi Agent API",
    description="Fullstack AI agent powered by Kimi (Moonshot AI) with web search, memory, and file analysis.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------------------------------- #
#  Routes                                                                       #
# --------------------------------------------------------------------------- #


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health():
    return HealthResponse(
        status="ok",
        model=os.getenv("KIMI_MODEL", "moonshot-v1-8k"),
    )


@app.post("/chat", response_model=ChatResponse, tags=["Agent"])
async def chat(request: ChatRequest):
    """Send a message to the Kimi agent. Optionally enables web search."""
    try:
        reply, sources = agent.chat(
            session_id=request.session_id,
            user_message=request.message,
            use_search=request.use_search,
        )
        return ChatResponse(
            session_id=request.session_id,
            reply=reply,
            sources=sources,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/upload", response_model=UploadResponse, tags=["Agent"])
async def upload_file(
    session_id: str = Form(...),
    file: UploadFile = File(...),
):
    """Upload a PDF, DOCX, or TXT file. The agent will analyse and summarise it."""
    allowed = {".pdf", ".docx", ".txt", ".md", ".csv"}
    ext = Path(file.filename or "").suffix.lower()

    if ext not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(allowed)}",
        )

    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        summary, file_type = agent.analyze_file(
            session_id=session_id,
            file_path=tmp_path,
            file_name=file.filename or "document",
        )
        return UploadResponse(
            session_id=session_id,
            file_name=file.filename or "document",
            message=f"Successfully processed {file_type.upper()} file.",
            summary=summary,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.unlink(tmp_path)


@app.get("/sessions/{session_id}/history", response_model=HistoryResponse, tags=["Memory"])
async def get_history(session_id: str):
    """Retrieve the full conversation history for a session."""
    memory = MemoryManager.get(session_id)
    raw = memory.get_messages_with_metadata()
    messages = [
        Message(
            role=m["role"],
            content=m["content"],
            timestamp=m.get("timestamp"),
        )
        for m in raw
    ]
    return HistoryResponse(
        session_id=session_id,
        messages=messages,
        total=len(messages),
    )


@app.delete("/sessions/{session_id}", tags=["Memory"])
async def clear_session(session_id: str):
    """Clear conversation memory for a session."""
    deleted = MemoryManager.delete(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found.")
    return {"message": f"Session '{session_id}' cleared."}


@app.get("/sessions/new", tags=["Memory"])
async def new_session():
    """Generate a new unique session ID."""
    return {"session_id": str(uuid.uuid4())}

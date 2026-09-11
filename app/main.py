from pathlib import Path
import os
import uuid
from typing import Optional
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.gemini import ask_gemini

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(title="CyberGuard AI", version="1.0.0")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# تخزين المحادثات في الذاكرة بدلاً من SQLite
chat_histories: dict[str, list[dict]] = {}


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=4000)


class ChatResponse(BaseModel):
    answer: str
    session_id: str


def get_history(session_id: str, limit: int = 20):
    return chat_histories.get(session_id, [])[-limit:]


def save_message(session_id: str, role: str, content: str):
    if session_id not in chat_histories:
        chat_histories[session_id] = []
    chat_histories[session_id].append({"role": role, "content": content})


@app.get("/")
def home():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "CyberGuard AI"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    history = get_history(req.session_id)

    try:
        answer = ask_gemini(req.message, history)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    save_message(req.session_id, "user", req.message)
    save_message(req.session_id, "model", answer)

    return ChatResponse(answer=answer, session_id=req.session_id)


@app.delete("/api/chat/{session_id}")
def clear_chat(session_id: str):
    chat_histories[session_id] = []
    return {"status": "cleared"}


@app.get("/api/history/{session_id}")
def history(session_id: str):
    return {"session_id": session_id, "messages": get_history(session_id, 100)}

from pathlib import Path
import os
import sqlite3
import uuid
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.gemini import ask_gemini

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "chat_history.db"

app = FastAPI(title="CyberGuard AI", version="1.0.0")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


init_db()


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=4000)


class ChatResponse(BaseModel):
    answer: str
    session_id: str


def get_history(session_id: str, limit: int = 20):
    conn = db()
    rows = conn.execute(
        """
        SELECT role, content FROM messages
        WHERE session_id = ?
        ORDER BY id ASC
        LIMIT ?
        """,
        (session_id, limit),
    ).fetchall()
    conn.close()
    return [{"role": row["role"], "content": row["content"]} for row in rows]


def save_message(session_id: str, role: str, content: str):
    conn = db()
    conn.execute(
        "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
        (session_id, role, content),
    )
    conn.commit()
    conn.close()


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
    conn = db()
    conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()
    return {"status": "cleared"}


@app.get("/api/history/{session_id}")
def history(session_id: str):
    return {"session_id": session_id, "messages": get_history(session_id, 100)}

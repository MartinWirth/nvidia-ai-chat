"""
NVIDIA AI Chat - FastAPI Backend

Nimmt Fragen vom Frontend entgegen, schickt sie an die NVIDIA-API
(OpenAI-kompatibler Endpunkt "integrate.api.nvidia.com") und gibt
die Antwort des Modells zurück.
"""

import os
from typing import List, Optional

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NVIDIA_API_BASE_URL = os.getenv(
    "NVIDIA_API_BASE_URL", "https://integrate.api.nvidia.com/v1"
)
DEFAULT_MODEL = os.getenv("NVIDIA_MODEL", "meta/llama-3.1-8b-instruct")

app = FastAPI(title="NVIDIA AI Chat", version="1.0.0")

# Erlaubt Zugriff vom lokal ausgelieferten Frontend (und für Entwicklung generell)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' oder 'assistant'")
    content: str


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Die Frage des Nutzers")
    model: Optional[str] = Field(default=None, description="Optional: anderes Modell verwenden")
    history: Optional[List[ChatMessage]] = Field(
        default=None, description="Optionaler bisheriger Gesprächsverlauf"
    )
    temperature: float = Field(default=0.5, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1024, ge=1, le=4096)


class ChatResponse(BaseModel):
    answer: str
    model: str


@app.get("/api/health")
async def health():
    return {"status": "ok", "api_key_configured": bool(NVIDIA_API_KEY)}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    if not NVIDIA_API_KEY:
        raise HTTPException(
            status_code=500,
            detail=(
                "Kein NVIDIA_API_KEY konfiguriert. Bitte .env Datei anlegen "
                "(siehe .env.example) und Server neu starten."
            ),
        )

    model = payload.model or DEFAULT_MODEL

    messages = []
    if payload.history:
        messages.extend({"role": m.role, "content": m.content} for m in payload.history)
    messages.append({"role": "user", "content": payload.question})

    request_body = {
        "model": model,
        "messages": messages,
        "temperature": payload.temperature,
        "max_tokens": payload.max_tokens,
    }

    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{NVIDIA_API_BASE_URL}/chat/completions",
                json=request_body,
                headers=headers,
            )
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=502, detail=f"Verbindung zur NVIDIA-API fehlgeschlagen: {exc}"
            )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"NVIDIA-API Fehler: {response.text}",
        )

    data = response.json()
    try:
        answer = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as exc:
        raise HTTPException(
            status_code=502, detail=f"Unerwartetes Antwortformat der NVIDIA-API: {exc}"
        )

    return ChatResponse(answer=answer, model=model)


# Statisches Frontend ausliefern (einfache HTML/JS-Oberfläche)
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def index():
    return FileResponse(os.path.join(static_dir, "index.html"))

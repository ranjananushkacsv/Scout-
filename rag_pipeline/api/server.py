"""
api/server.py — FastAPI app tying together the dashboard, chat, and
escalation endpoints for the Scout frontend.

Run from the rag_pipeline/ directory:
    uvicorn api.server:app --reload --port 8000
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import chat, dashboard, escalations

app = FastAPI(title="Scout API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router)
app.include_router(chat.router)
app.include_router(escalations.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}

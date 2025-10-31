from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.api.v1 import types, states, operations, save_all

app = FastAPI(title="Process Manager API", version="1.0.0")

# CORS for React frontend
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://process-manager-frontend.onrender.com",
]

# Add production frontend URL if available
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url and frontend_url not in allowed_origins:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(types.router, prefix="/api/v1", tags=["types"])
app.include_router(states.router, prefix="/api/v1", tags=["states"])
app.include_router(operations.router, prefix="/api/v1", tags=["operations"])
app.include_router(save_all.router, prefix="/api/v1", tags=["save-all"])


@app.get("/health")
def health_check():
    return {"status": "ok"}


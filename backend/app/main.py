"""
Autonomous AI Agent Platform - Main FastAPI Application

This is the entry point for the backend server.
Run with: uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ─── Import models (so tables get registered) ───
from app.models.goal import Goal
from app.models.task import Task
from app.models.agent import Agent
from app.models.approval import Approval

# ─── Import routers ───
from app.api.v1.goals import router as goals_router
from app.api.v1.tasks import router as tasks_router
# ─── Create FastAPI app ───
app = FastAPI(
    title="Autonomous AI Agent Platform",
    description="AI-powered autonomous agent platform with multi-agent collaboration",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── CORS Middleware ───
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Include Routers ───
app.include_router(goals_router)
app.include_router(tasks_router)

# ─── Health Check Endpoints ───
@app.get("/", tags=["health"])
async def root():
    """Root endpoint - basic info"""
    return {
        "message": "Autonomous AI Agent Platform API",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "backend",
    }


@app.get("/api/v1/ping", tags=["test"])
async def ping():
    """Simple ping endpoint to test API"""
    return {"pong": True}

"""
Autonomous AI Agent Platform - Main FastAPI Application

This is the entry point for the backend server.
Run with: uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ─── Create FastAPI app ───
app = FastAPI(
    title="Autonomous AI Agent Platform",
    description="AI-powered autonomous agent platform with multi-agent collaboration",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── CORS Middleware (allow frontend to talk to backend) ───
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Health Check Endpoint ───
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


# ─── Test Endpoint ───
@app.get("/api/v1/ping", tags=["test"])
async def ping():
    """Simple ping endpoint to test API"""
    return {"pong": True}

"""
FastAPI server for Whisper AI API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import routes
from api.routes import upload, transcribe, download

# Create FastAPI app
app = FastAPI(
    title="Whisper AI API",
    description="API for audio/video transcription using Whisper AI",
    version="1.0.0"
)

# Setup CORS directly
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js development server
        "http://localhost:3001",  # Alternative Next.js port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "*",  # Allow all origins for development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router)
app.include_router(transcribe.router)
app.include_router(download.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Whisper AI API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/api/upload",
            "transcribe": "/api/transcribe",
            "download": "/api/download",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 
"""
Transcription endpoint for Whisper AI API
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import sys
import os

# Add the parent directory to the path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.transcriber import WhisperTranscriber
from src.audio_processor import AudioProcessor
from src.output_formatter import OutputFormatter
from api.utils.file_handler import FileHandler

router = APIRouter(prefix="/api", tags=["transcribe"])

# Initialize components
transcriber = WhisperTranscriber()
audio_processor = AudioProcessor()
output_formatter = OutputFormatter()
file_handler = FileHandler()


class TranscriptionRequest(BaseModel):
    """Request model for transcription"""
    file_path: str
    model: str = "base"
    language: str = "auto"
    task: str = "transcribe"


class TranscriptionResponse(BaseModel):
    """Response model for transcription"""
    success: bool
    message: str
    text: str = ""
    segments: List[Dict[str, Any]] = []
    language: str = ""
    confidence: float = 0.0
    processing_time: float = 0.0
    model_used: str = ""
    file_path: str = ""
    error: str = None


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_file(request: TranscriptionRequest):
    """
    Transcribe audio/video file
    
    Args:
        request: TranscriptionRequest with file path and options
        
    Returns:
        TranscriptionResponse with transcription results
    """
    try:
        # Validate file exists
        if not os.path.exists(request.file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Validate file using existing backend
        is_valid, error_msg = audio_processor.validate_file(request.file_path)
        if not is_valid:
            return TranscriptionResponse(
                success=False,
                message="File validation failed",
                error=error_msg
            )
        
        # Prepare audio for transcription using existing backend
        success, audio_path = audio_processor.prepare_audio_for_whisper(request.file_path)
        if not success:
            return TranscriptionResponse(
                success=False,
                message="Audio preparation failed",
                error=audio_path
            )
        
        # Perform transcription using existing backend
        result = transcriber.transcribe_audio(
            audio_path=audio_path,
            language=request.language if request.language != "auto" else None,
            task=request.task,
            model=request.model
        )
        
        if not result.get("success", False):
            return TranscriptionResponse(
                success=False,
                message="Transcription failed",
                error=result.get("error", "Unknown error")
            )
        
        # Format response
        return TranscriptionResponse(
            success=True,
            message="Transcription completed successfully",
            text=result.get("text", ""),
            segments=result.get("segments", []),
            language=result.get("language", ""),
            confidence=result.get("confidence", 0.0),
            processing_time=result.get("processing_time", 0.0),
            model_used=result.get("model_used", ""),
            file_path=result.get("file_path", "")
        )
        
    except Exception as e:
        return TranscriptionResponse(
            success=False,
            message="Transcription failed",
            error=str(e)
        )


@router.post("/detect-language")
async def detect_language(request: TranscriptionRequest):
    """
    Detect language of audio/video file
    
    Args:
        request: TranscriptionRequest with file path
        
    Returns:
        Dictionary with language detection results
    """
    try:
        # Validate file exists
        if not os.path.exists(request.file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Validate file using existing backend
        is_valid, error_msg = audio_processor.validate_file(request.file_path)
        if not is_valid:
            return {
                "success": False,
                "error": error_msg
            }
        
        # Prepare audio for transcription
        success, audio_path = audio_processor.prepare_audio_for_whisper(request.file_path)
        if not success:
            return {
                "success": False,
                "error": audio_path
            }
        
        # Detect language using existing backend
        result = transcriber.detect_language(audio_path)
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/models")
async def get_available_models():
    """
    Get list of available Whisper models
    
    Returns:
        Dictionary with available models
    """
    return {
        "available_models": ["tiny", "base", "small", "medium", "large"],
        "default_model": "base"
    } 
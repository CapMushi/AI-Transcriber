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
from api.utils.vector_handler import VectorHandler

router = APIRouter(prefix="/api", tags=["transcribe"])

# Initialize components
transcriber = WhisperTranscriber()
audio_processor = AudioProcessor()
output_formatter = OutputFormatter()
file_handler = FileHandler()
vector_handler = VectorHandler()


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
    storage_status: Dict[str, Any] = None


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
        
        # PHASE 2: Store chunks in Pinecone (non-blocking)
        storage_status = None
        try:
            # Get file information for metadata
            file_info = audio_processor.get_file_info(request.file_path)
            
            # Generate unique file ID
            file_id = vector_handler.generate_file_id()
            
            # Prepare file metadata
            file_metadata = vector_handler.prepare_file_metadata(
                original_filename=os.path.basename(request.file_path),
                file_info=file_info
            )
            
            # Store chunks in Pinecone (non-blocking)
            storage_result = await vector_handler.store_transcription_chunks(
                file_id=file_id,
                transcription_data=result,
                file_metadata=file_metadata
            )
            
            storage_status = {
                "success": storage_result.get("success", False),
                "message": storage_result.get("message", ""),
                "file_id": file_id,
                "chunks_stored": storage_result.get("chunks_stored", 0)
            }
            
            if storage_result.get("success", False):
                print(f"✅ Stored {storage_result.get('chunks_stored', 0)} chunks in Pinecone for file {file_id}")
            else:
                print(f"⚠️ Pinecone storage failed: {storage_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"⚠️ Pinecone storage error: {e}")
            storage_status = {
                "success": False,
                "message": f"Storage error: {str(e)}",
                "file_id": None,
                "chunks_stored": 0
            }
        
        # Format response (existing functionality unchanged)
        return TranscriptionResponse(
            success=True,
            message="Transcription completed successfully",
            text=result.get("text", ""),
            segments=result.get("segments", []),
            language=result.get("language", ""),
            confidence=result.get("confidence", 0.0),
            processing_time=result.get("processing_time", 0.0),
            model_used=result.get("model_used", ""),
            file_path=result.get("file_path", ""),
            storage_status=storage_status
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


@router.get("/storage-status")
async def get_storage_status():
    """
    Get Pinecone storage status
    
    Returns:
        Dictionary with storage configuration status
    """
    try:
        status = vector_handler.get_storage_status()
        return status
    except Exception as e:
        return {
            "success": False,
            "error": f"Status check failed: {str(e)}"
        } 
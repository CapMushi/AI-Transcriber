"""
File upload endpoint for Whisper AI API
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import sys
import os
from pathlib import Path

# Add the parent directory to the path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.audio_processor import AudioProcessor
from api.utils.file_handler import FileHandler

router = APIRouter(prefix="/api", tags=["upload"])

# Initialize components
audio_processor = AudioProcessor()
file_handler = FileHandler()


class UploadResponse(BaseModel):
    """Response model for file upload"""
    success: bool
    message: str
    file_info: Dict[str, Any] = None
    error: str = None


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and validate audio/video file
    
    Args:
        file: Uploaded file
        
    Returns:
        UploadResponse with validation results
    """
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        file_extension = Path(file.filename).suffix.lower()
        supported_formats = audio_processor.supported_audio_formats + audio_processor.supported_video_formats
        
        if file_extension not in supported_formats:
            return UploadResponse(
                success=False,
                message="File validation failed",
                error=f"Unsupported file format: {file_extension}. Supported formats: {supported_formats}"
            )
        
        # Save uploaded file
        success, result = await file_handler.save_uploaded_file(file)
        if not success:
            return UploadResponse(
                success=False,
                message="File upload failed",
                error=result
            )
        
        file_path = result
        
        # Validate file using existing backend
        is_valid, error_msg = audio_processor.validate_file(file_path)
        if not is_valid:
            # Clean up invalid file
            file_handler.cleanup_file(file_path)
            return UploadResponse(
                success=False,
                message="File validation failed",
                error=error_msg
            )
        
        # Get file information using existing backend
        file_info = audio_processor.get_file_info(file_path)
        
        return UploadResponse(
            success=True,
            message="File uploaded and validated successfully",
            file_info={
                "file_path": file_path,
                "original_name": file.filename,
                "size_mb": file_info.get("size_mb", 0),
                "duration": file_info.get("duration", 0),
                "format": file_info.get("extension", ""),
                "is_audio": file_info.get("is_audio", False),
                "is_video": file_info.get("is_video", False)
            }
        )
        
    except Exception as e:
        return UploadResponse(
            success=False,
            message="Upload failed",
            error=str(e)
        )


@router.get("/supported-formats")
async def get_supported_formats():
    """
    Get list of supported file formats
    
    Returns:
        Dictionary with supported formats
    """
    return {
        "audio_formats": audio_processor.supported_audio_formats,
        "video_formats": audio_processor.supported_video_formats,
        "max_file_size_mb": audio_processor.max_file_size_mb
    } 
"""
Download endpoint for Whisper AI API
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import sys
import os
import tempfile
from pathlib import Path

# Add the parent directory to the path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.output_formatter import OutputFormatter

router = APIRouter(prefix="/api", tags=["download"])

# Initialize components
output_formatter = OutputFormatter()


class DownloadRequest(BaseModel):
    """Request model for download"""
    transcription_data: Dict[str, Any]
    format: str = "txt"
    filename: str = "transcription"


@router.post("/download")
async def download_transcription(request: DownloadRequest):
    """
    Download transcription in specified format
    
    Args:
        request: DownloadRequest with transcription data and format
        
    Returns:
        FileResponse with downloadable file
    """
    try:
        # Validate format
        if request.format not in output_formatter.supported_formats:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported format: {request.format}. Supported formats: {output_formatter.supported_formats}"
            )
        
        # Format the transcription data
        formatted_content = output_formatter.format_transcription_result(
            request.transcription_data, 
            request.format
        )
        
        # Create temporary file
        temp_dir = tempfile.gettempdir()
        file_extension = {
            "txt": ".txt",
            "json": ".json", 
            "srt": ".srt"
        }.get(request.format, ".txt")
        
        temp_filename = f"{request.filename}{file_extension}"
        temp_path = Path(temp_dir) / temp_filename
        
        # Write formatted content to file
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(formatted_content)
        
        # Return file response
        return FileResponse(
            path=str(temp_path),
            filename=temp_filename,
            media_type='application/octet-stream'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@router.get("/formats")
async def get_available_formats():
    """
    Get list of available download formats
    
    Returns:
        Dictionary with available formats
    """
    return {
        "available_formats": output_formatter.supported_formats,
        "default_format": output_formatter.default_format
    } 
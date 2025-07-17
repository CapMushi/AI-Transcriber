"""
File handling utilities for Whisper AI API
"""

import os
import tempfile
import uuid
from pathlib import Path
from typing import Optional, Tuple
from fastapi import UploadFile


class FileHandler:
    """Handles file uploads and temporary file management"""
    
    def __init__(self, temp_dir: str = None):
        """
        Initialize file handler
        
        Args:
            temp_dir: Directory for temporary files (default: system temp)
        """
        self.temp_dir = temp_dir or tempfile.gettempdir()
        self.upload_dir = Path(self.temp_dir) / "whisper_uploads"
        self.upload_dir.mkdir(exist_ok=True)
    
    async def save_uploaded_file(self, file: UploadFile) -> Tuple[bool, str]:
        """
        Save uploaded file to temporary directory
        
        Args:
            file: Uploaded file from FastAPI
            
        Returns:
            Tuple of (success, file_path or error_message)
        """
        try:
            # Generate unique filename
            file_id = str(uuid.uuid4())
            file_extension = Path(file.filename).suffix if file.filename else ""
            temp_filename = f"{file_id}{file_extension}"
            temp_path = self.upload_dir / temp_filename
            
            # Save file
            with open(temp_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            return True, str(temp_path)
            
        except Exception as e:
            return False, f"Error saving file: {str(e)}"
    
    def cleanup_file(self, file_path: str) -> bool:
        """
        Clean up temporary file
        
        Args:
            file_path: Path to file to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception:
            return False
    
    def get_file_info(self, file_path: str) -> dict:
        """
        Get basic information about a file
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file information
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return {"error": "File not found"}
            
            return {
                "path": str(path),
                "name": path.name,
                "size_bytes": path.stat().st_size,
                "size_mb": path.stat().st_size / (1024 * 1024),
                "extension": path.suffix.lower(),
                "exists": True
            }
        except Exception as e:
            return {"error": str(e)}
    
    def cleanup_old_files(self, max_age_hours: int = 24) -> int:
        """
        Clean up old temporary files
        
        Args:
            max_age_hours: Maximum age of files in hours
            
        Returns:
            Number of files cleaned up
        """
        import time
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        cleaned_count = 0
        
        try:
            for file_path in self.upload_dir.glob("*"):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        cleaned_count += 1
        except Exception:
            pass
        
        return cleaned_count 
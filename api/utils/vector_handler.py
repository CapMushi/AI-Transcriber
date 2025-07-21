"""
API-level vector operations for Whisper AI API
"""

import uuid
from typing import Dict, Any, Optional
from datetime import datetime
import sys
import os
from pathlib import Path

# Add the parent directory to the path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.vector_store import PineconeVectorStore


class VectorHandler:
    """Handles vector operations at the API level"""
    
    def __init__(self):
        """Initialize vector handler"""
        self.vector_store = PineconeVectorStore()
    
    def generate_file_id(self) -> str:
        """
        Generate a unique file ID
        
        Returns:
            Unique file identifier
        """
        return str(uuid.uuid4())
    
    async def store_transcription_chunks(self,
                                       file_id: str,
                                       transcription_data: Dict[str, Any],
                                       file_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store transcription chunks in Pinecone (non-blocking)
        
        Args:
            file_id: Unique identifier for the file
            transcription_data: Transcription result from Whisper
            file_metadata: File information metadata
            
        Returns:
            Dictionary with storage result
        """
        try:
            # Validate that we have transcription data
            if not transcription_data.get("success", False):
                return {
                    "success": False,
                    "error": "No successful transcription data to store"
                }
            
            # Validate that we have segments
            segments = transcription_data.get("segments", [])
            if not segments:
                return {
                    "success": False,
                    "error": "No segments found in transcription data"
                }
            
            # Store chunks in Pinecone
            success = self.vector_store.store_transcription_chunks(
                file_id=file_id,
                transcription_data=transcription_data,
                file_metadata=file_metadata
            )
            
            if success:
                return {
                    "success": True,
                    "message": f"Stored transcription chunks for file {file_id}",
                    "file_id": file_id,
                    "chunks_stored": len(segments)
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to store chunks in Pinecone"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Vector storage error: {str(e)}"
            }
    
    def search_transcriptions(self,
                            query: str,
                            top_k: int = 5,
                            filter_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Search for transcription chunks
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Metadata filters
            
        Returns:
            Dictionary with search results
        """
        try:
            results = self.vector_store.search_chunks(
                query=query,
                top_k=top_k,
                filter_metadata=filter_metadata
            )
            
            return {
                "success": True,
                "query": query,
                "results": results,
                "count": len(results)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Search failed: {str(e)}",
                "query": query,
                "results": []
            }
    
    def get_storage_status(self) -> Dict[str, Any]:
        """
        Get Pinecone storage status
        
        Returns:
            Dictionary with storage status
        """
        try:
            is_valid = self.vector_store.validate_configuration()
            
            return {
                "success": True,
                "pinecone_configured": bool(self.vector_store.api_key),
                "openai_configured": bool(self.vector_store.openai_client),
                "index_name": self.vector_store.index_name,
                "environment": self.vector_store.environment,
                "configuration_valid": is_valid
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Status check failed: {str(e)}"
            }
    
    def prepare_file_metadata(self, 
                            original_filename: str,
                            file_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare file metadata for vector storage
        
        Args:
            original_filename: Original uploaded filename
            file_info: File information from audio processor
            
        Returns:
            Prepared metadata dictionary
        """
        return {
            "original_name": original_filename,
            "size_mb": file_info.get("size_mb", 0),
            "duration": file_info.get("duration", 0),
            "extension": file_info.get("extension", ""),
            "is_audio": file_info.get("is_audio", False),
            "is_video": file_info.get("is_video", False),
            "sample_rate": file_info.get("sample_rate", 0),
            "channels": file_info.get("channels", 0),
            "codec": file_info.get("codec", "unknown")
        } 
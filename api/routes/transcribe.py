"""
Transcription endpoint for Whisper AI API
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional, Tuple
import sys
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

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
    use_parallel: bool = False  # NEW: Enable parallel processing


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
    parallel_used: bool = False  # NEW: Indicates if parallel processing was used


class ComparisonRequest(BaseModel):
    """Request model for content comparison"""
    primary_file_path: str
    secondary_file_path: str
    threshold: float = 0.7  # Lowered from 0.95 to 0.7 for testing
    model: str = "base"
    language: str = "auto"
    use_parallel: bool = False  # NEW: Enable parallel processing


class ComparisonResponse(BaseModel):
    """Response model for content comparison"""
    success: bool
    message: str
    found: bool = False
    timestamps: List[Dict[str, float]] = []  # start/end times
    confidence: float = 0.0
    primary_text: str = ""
    secondary_text: str = ""
    error: str = None
    parallel_used: bool = False  # NEW: Indicates if parallel processing was used


class StorePrimaryRequest(BaseModel):
    """Request model for storing primary content"""
    file_path: str
    model: str = "base"
    language: str = "auto"
    use_parallel: bool = False  # NEW: Enable parallel processing


class StorePrimaryResponse(BaseModel):
    """Response model for storing primary content"""
    success: bool
    message: str
    file_id: str = ""
    chunks_stored: int = 0
    text: str = ""
    segments: List[Dict[str, Any]] = []
    error: str = None
    storage_in_progress: bool = False  # NEW: Indicates if storage is happening in background
    parallel_used: bool = False  # NEW: Indicates if parallel processing was used


def _transcribe_single_file(file_path: str, model: str, language: str, task: str) -> Dict[str, Any]:
    """Helper function for single file transcription (for parallel processing)"""
    try:
        # Validate file
        is_valid, error_msg = audio_processor.validate_file(file_path)
        if not is_valid:
            return {"success": False, "error": error_msg}
        
        # Prepare audio
        success, prepared_audio = audio_processor.prepare_audio_for_whisper_fast(file_path)
        if not success:
            return {"success": False, "error": prepared_audio}
        
        # Transcribe
        transcription_result = transcriber.transcribe_audio(
            prepared_audio, 
            language=language, 
            task=task
        )
        
        if not transcription_result["success"]:
            return transcription_result
        
        return {
            "success": True,
            "text": transcription_result["text"],
            "segments": transcription_result["segments"],
            "language": transcription_result["language"],
            "confidence": transcription_result["confidence"],
            "processing_time": transcription_result["processing_time"],
            "model_used": model,
            "file_path": file_path
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


async def _transcribe_parallel(files: List[Tuple[str, str, str, str]], max_workers: int = 2) -> List[Dict[str, Any]]:
    """Transcribe multiple files in parallel"""
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all transcription tasks
        future_to_file = {
            executor.submit(_transcribe_single_file, file_path, model, language, task): (file_path, model, language, task)
            for file_path, model, language, task in files
        }
        
        # Collect results as they complete
        for future in asyncio.as_completed([future_to_file[f] for f in future_to_file.keys()]):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                results.append({"success": False, "error": str(e)})
    
    return results


# Background storage function
async def _store_primary_content_background(
    file_id: str,
    transcription_data: Dict[str, Any],
    file_metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Background function to store primary content in Pinecone
    
    Args:
        file_id: Unique identifier for the file
        transcription_data: Transcription result from Whisper
        file_metadata: File information metadata
        
    Returns:
        Dictionary with storage result
    """
    try:
        print(f"🔄 Background storage started for file {file_id}")
        
        # Store primary content (clearing existing embeddings)
        storage_result = await vector_handler.store_primary_content(
            file_id=file_id,
            transcription_data=transcription_data,
            file_metadata=file_metadata
        )
        
        print(f"🔄 Background storage completed for file {file_id}: {storage_result}")
        return storage_result
        
    except Exception as e:
        print(f"❌ Background storage failed for file {file_id}: {e}")
        return {
            "success": False,
            "error": f"Background storage failed: {str(e)}"
        }


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
        # Use parallel processing if requested
        if request.use_parallel:
            # For single file, parallel processing is not beneficial
            # But we'll use the parallel infrastructure for consistency
            files = [(request.file_path, request.model, request.language, request.task)]
            results = await _transcribe_parallel(files, max_workers=1)
            
            if not results or not results[0]["success"]:
                error_msg = results[0].get("error", "Unknown error") if results else "No results"
                return TranscriptionResponse(
                    success=False,
                    message=f"Parallel transcription failed: {error_msg}",
                    error=error_msg,
                    parallel_used=True
                )
            
            result = results[0]
            
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
            
            return TranscriptionResponse(
                success=True,
                message="Parallel transcription completed successfully",
                text=result["text"],
                segments=result["segments"],
                language=result["language"],
                confidence=result["confidence"],
                processing_time=result["processing_time"],
                model_used=result["model_used"],
                file_path=result["file_path"],
                storage_status=storage_status,
                parallel_used=True
            )
        
        # Standard sequential processing
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
        
        # Prepare audio for transcription using optimized backend
        success, audio_path = audio_processor.prepare_audio_for_whisper_fast(request.file_path)
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
            storage_status=storage_status,
            parallel_used=False
        )
        
    except Exception as e:
        return TranscriptionResponse(
            success=False,
            message="Transcription failed",
            error=str(e)
        )


@router.post("/store-primary", response_model=StorePrimaryResponse)
async def store_primary_content(request: StorePrimaryRequest):
    """
    Store primary content in Pinecone (clearing existing embeddings first)
    Returns transcription immediately, then stores in background
    
    Args:
        request: StorePrimaryRequest with file path and options
        
    Returns:
        StorePrimaryResponse with transcription results and storage status
    """
    try:
        # Validate file exists
        if not os.path.exists(request.file_path):
            return StorePrimaryResponse(
                success=False,
                message="File not found",
                error=f"File not found: {request.file_path}"
            )
        
        # Validate file using existing backend
        is_valid, error_msg = audio_processor.validate_file(request.file_path)
        if not is_valid:
            return StorePrimaryResponse(
                success=False,
                message="File validation failed",
                error=error_msg
            )
        
        # Prepare audio for transcription using optimized backend
        success, audio_path = audio_processor.prepare_audio_for_whisper_fast(request.file_path)
        if not success:
            return StorePrimaryResponse(
                success=False,
                message="Audio preparation failed",
                error=audio_path
            )
        
        # Transcribe file using existing backend
        result = transcriber.transcribe_audio(
            audio_path=audio_path,
            language=request.language if request.language != "auto" else None,
            task="transcribe",
            model=request.model
        )
        
        if not result.get("success", False):
            return StorePrimaryResponse(
                success=False,
                message="Transcription failed",
                error=result.get("error", "Unknown error")
            )
        
        # Return transcription results immediately
        file_id = vector_handler.generate_file_id()
        
        # Start background storage operation
        try:
            # Get file information for metadata
            file_info = audio_processor.get_file_info(request.file_path)
            
            # Prepare file metadata
            original_filename = os.path.basename(request.file_path)
            print(f"🔍 DEBUG: store-primary API route preparing metadata:")
            print(f"  - request.file_path: '{request.file_path}'")
            print(f"  - os.path.basename result: '{original_filename}'")
            print(f"  - file_info: {file_info}")
            
            file_metadata = vector_handler.prepare_file_metadata(
                original_filename=original_filename,
                file_info=file_info
            )
            
            # Start background storage task
            asyncio.create_task(
                _store_primary_content_background(
                    file_id=file_id,
                    transcription_data=result,
                    file_metadata=file_metadata
                )
            )
            
            # Return success response with transcription immediately
            return StorePrimaryResponse(
                success=True,
                message="Transcription completed. Storage in progress...",
                file_id=file_id,
                chunks_stored=0,  # Will be updated in background
                text=result.get("text", ""),
                segments=result.get("segments", []),
                storage_in_progress=True  # Indicates background storage is happening
            )
                
        except Exception as e:
            # Even if background storage fails, return transcription results
            return StorePrimaryResponse(
                success=True,
                message="Transcription completed. Storage failed.",
                file_id=file_id,
                chunks_stored=0,
                text=result.get("text", ""),
                segments=result.get("segments", []),
                storage_in_progress=False,
                error=f"Storage failed: {str(e)}"
            )
        
    except Exception as e:
        return StorePrimaryResponse(
            success=False,
            message="Store primary content failed",
            error=str(e)
        )


@router.post("/compare-content", response_model=ComparisonResponse)
async def compare_content(request: ComparisonRequest):
    """
    Compare secondary video/audio content against already-stored primary content
    
    Args:
        request: ComparisonRequest with primary and secondary file paths
        
    Returns:
        ComparisonResponse with comparison results and timestamps
    """
    try:
        # Use parallel processing if requested
        if request.use_parallel:
            # For comparison, we only need to transcribe the secondary file
            # Parallel processing is not beneficial for single file
            # But we'll use the parallel infrastructure for consistency
            files = [(request.secondary_file_path, request.model, request.language, "transcribe")]
            results = await _transcribe_parallel(files, max_workers=1)
            
            if not results or not results[0]["success"]:
                error_msg = results[0].get("error", "Unknown error") if results else "No results"
                return ComparisonResponse(
                    success=False,
                    message=f"Parallel secondary transcription failed: {error_msg}",
                    error=error_msg,
                    parallel_used=True
                )
            
            secondary_result = results[0]
            
            # Search for secondary content in already-stored primary content
            try:
                print(f"🔍 DEBUG: API calling search_content_matches_optimized with threshold={request.threshold}")
                print(f"🔍 DEBUG: Secondary result: {secondary_result.get('text', '')[:100]}...")
                
                search_result = await vector_handler.search_content_matches_optimized(
                    secondary_transcription=secondary_result,
                    threshold=request.threshold
                )
                
                print(f"🔍 DEBUG: API search result: {search_result}")
                
                if search_result.get("success", False):
                    matches = search_result.get("matches", [])
                    if matches:
                        # Content found - return timestamps
                        # Extract only timestamp fields from matches
                        timestamp_data = []
                        for match in matches:
                            timestamp_data.append({
                                "start_time": match.get("start_time", 0.0),
                                "end_time": match.get("end_time", 0.0)
                            })
                        
                        return ComparisonResponse(
                            success=True,
                            message="Content found in primary (parallel processing)",
                            found=True,
                            timestamps=timestamp_data,
                            confidence=search_result.get("confidence", 0.0),
                            primary_text="",  # No primary text since it's already stored
                            secondary_text=secondary_result.get("text", ""),
                            parallel_used=True
                        )
                    else:
                        # Content not found
                        return ComparisonResponse(
                            success=True,
                            message="Secondary content not found in primary with specified threshold (parallel processing)",
                            found=False,
                            primary_text="",  # No primary text since it's already stored
                            secondary_text=secondary_result.get("text", ""),
                            parallel_used=True
                        )
                else:
                    return ComparisonResponse(
                        success=False,
                        message="Content search failed",
                        error=search_result.get("error", "Unknown error"),
                        parallel_used=True
                    )
                    
            except Exception as e:
                return ComparisonResponse(
                    success=False,
                    message="Content comparison failed",
                    error=str(e),
                    parallel_used=True
                )
        
        # Standard sequential processing
        # Validate secondary file exists
        if not os.path.exists(request.secondary_file_path):
            return ComparisonResponse(
                success=False,
                message="Secondary file not found",
                error=f"File not found: {request.secondary_file_path}"
            )
        
        # Validate secondary file using existing backend
        secondary_valid, secondary_error = audio_processor.validate_file(request.secondary_file_path)
        if not secondary_valid:
            return ComparisonResponse(
                success=False,
                message="Secondary file validation failed",
                error=secondary_error
            )
        
        # Prepare audio for secondary file using optimized backend
        secondary_success, secondary_audio_path = audio_processor.prepare_audio_for_whisper_fast(request.secondary_file_path)
        if not secondary_success:
            return ComparisonResponse(
                success=False,
                message="Secondary audio preparation failed",
                error=secondary_audio_path
            )
        
        # Transcribe secondary file (no storage needed)
        secondary_result = transcriber.transcribe_audio(
            audio_path=secondary_audio_path,
            language=request.language if request.language != "auto" else None,
            task="transcribe",
            model=request.model
        )
        
        if not secondary_result.get("success", False):
            return ComparisonResponse(
                success=False,
                message="Secondary transcription failed",
                error=secondary_result.get("error", "Unknown error")
            )
        
        # Search for secondary content in already-stored primary content
        try:
            print(f"🔍 DEBUG: API calling search_content_matches_optimized with threshold={request.threshold}")
            print(f"🔍 DEBUG: Secondary result: {secondary_result.get('text', '')[:100]}...")
            
            search_result = await vector_handler.search_content_matches_optimized(
                secondary_transcription=secondary_result,
                threshold=request.threshold
            )
            
            print(f"🔍 DEBUG: API search result: {search_result}")
            
            if search_result.get("success", False):
                matches = search_result.get("matches", [])
                if matches:
                    # Content found - return timestamps
                    # Extract only timestamp fields from matches
                    timestamp_data = []
                    for match in matches:
                        timestamp_data.append({
                            "start_time": match.get("start_time", 0.0),
                            "end_time": match.get("end_time", 0.0)
                        })
                    
                    return ComparisonResponse(
                        success=True,
                        message="Content found in primary",
                        found=True,
                        timestamps=timestamp_data,
                        confidence=search_result.get("confidence", 0.0),
                        primary_text="",  # No primary text since it's already stored
                        secondary_text=secondary_result.get("text", ""),
                        parallel_used=False
                    )
                else:
                    # Content not found
                    return ComparisonResponse(
                        success=True,
                        message="Secondary content not found in primary with specified threshold",
                        found=False,
                        primary_text="",  # No primary text since it's already stored
                        secondary_text=secondary_result.get("text", ""),
                        parallel_used=False
                    )
            else:
                return ComparisonResponse(
                    success=False,
                    message="Content search failed",
                    error=search_result.get("error", "Unknown error"),
                    parallel_used=False
                )
                
        except Exception as e:
            return ComparisonResponse(
                success=False,
                message="Content comparison failed",
                error=str(e),
                parallel_used=False
            )
        
    except Exception as e:
        return ComparisonResponse(
            success=False,
            message="Comparison failed",
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
        
        # Prepare audio for transcription using optimized backend
        success, audio_path = audio_processor.prepare_audio_for_whisper_fast(request.file_path)
        if not success:
            return {
                "success": False,
                "error": audio_path
            }
        
        # Detect language using existing backend
        language_result = transcriber.detect_language(audio_path)
        
        if language_result.get("success", False):
            return {
                "success": True,
                "detected_language": language_result.get("detected_language"),
                "language_probabilities": language_result.get("language_probabilities", {})
            }
        else:
            return {
                "success": False,
                "error": language_result.get("error", "Language detection failed")
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/models")
async def get_available_models():
    """Get available Whisper models"""
    return {
        "models": ["tiny", "base", "small", "medium", "large"],
        "default_model": "base",
        "description": "Available Whisper models for transcription"
    }


@router.get("/storage-status")
async def get_storage_status():
    """Get Pinecone storage status"""
    return vector_handler.get_storage_status()


class ClearEmbeddingsResponse(BaseModel):
    """Response model for clear embeddings"""
    success: bool
    message: str
    error: str = None


@router.post("/clear-embeddings", response_model=ClearEmbeddingsResponse)
async def clear_embeddings():
    """Manually clear all embeddings from Pinecone"""
    try:
        success = vector_handler.clear_embeddings()
        if success:
            return ClearEmbeddingsResponse(
                success=True,
                message="Successfully cleared all embeddings from Pinecone"
            )
        else:
            return ClearEmbeddingsResponse(
                success=False,
                error="Failed to clear embeddings"
            )
    except Exception as e:
        return ClearEmbeddingsResponse(
            success=False,
            error=f"Clear embeddings error: {str(e)}"
        ) 
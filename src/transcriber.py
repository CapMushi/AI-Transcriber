"""
Whisper transcription module for Whisper AI Transcription Project
"""

import whisper
import time
import os
from pathlib import Path
from typing import Union, Dict, Any, Optional
import config


class WhisperTranscriber:
    """Handles Whisper model loading and transcription"""
    
    # Class-level model cache to avoid reloading
    _model_cache = {}
    
    def __init__(self, model_name: str = None):
        """
        Initialize the Whisper transcriber
        
        Args:
            model_name: Name of the Whisper model to use (default: config.DEFAULT_MODEL)
        """
        self.model_name = model_name or config.DEFAULT_MODEL
        self.model = None
        self.model_loaded = False
        
        # Set FFmpeg path for Whisper
        if "C:\\ffmpeg\\bin" not in os.environ.get("PATH", ""):
            os.environ["PATH"] = os.environ.get("PATH", "") + ";C:\\ffmpeg\\bin"
    
    def load_model(self) -> bool:
        """
        Load the Whisper model with caching
        
        Returns:
            True if model loaded successfully, False otherwise
        """
        try:
            # Check if model is already cached
            if self.model_name in self._model_cache:
                print(f"Using cached model: {self.model_name}")
                self.model = self._model_cache[self.model_name]
                self.model_loaded = True
                return True
            
            # Load model and cache it
            print(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(self.model_name)
            self._model_cache[self.model_name] = self.model
            self.model_loaded = True
            print(f"Model {self.model_name} loaded and cached successfully")
            return True
        except Exception as e:
            print(f"Error loading model {self.model_name}: {str(e)}")
            self.model_loaded = False
            return False
    
    def transcribe_audio(self, audio_path: Union[str, Path], 
                        language: str = None,
                        task: str = "transcribe",
                        model: str = None) -> Dict[str, Any]:
        """
        Transcribe audio file using Whisper
        
        Args:
            audio_path: Path to the audio file
            language: Language code (None for auto-detection)
            task: Task type ("transcribe" or "translate")
            model: Model to use (if different from current)
            
        Returns:
            Dictionary containing transcription results
        """
        # Load new model if specified and different from current
        if model and model != self.model_name:
            print(f"Switching to model: {model}")
            self.model_name = model
            self.model_loaded = False
        
        if not self.model_loaded:
            if not self.load_model():
                return {"error": "Failed to load Whisper model"}
        
        try:
            audio_path = Path(audio_path)
            
            # Start timing
            start_time = time.time()
            
            # Prepare transcription options
            options = {}
            if language and language != "auto":
                options["language"] = language
            if task == "translate":
                options["task"] = "translate"
            
            # Perform transcription
            print(f"Transcribing: {audio_path.name}")
            result = self.model.transcribe(str(audio_path), **options)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Calculate confidence from segments
            segments = result.get("segments", [])
            confidence = 0.0
            if segments:
                # Calculate average confidence from all segments
                total_confidence = 0.0
                for segment in segments:
                    # Convert avg_logprob to confidence percentage
                    # avg_logprob is typically negative, closer to 0 means higher confidence
                    avg_logprob = segment.get("avg_logprob", -1.0)
                    # Convert log probability to confidence (0-100%)
                    # Formula: confidence = max(0, (avg_logprob + 1) * 100)
                    segment_confidence = max(0, min(100, (avg_logprob + 1) * 100))
                    total_confidence += segment_confidence
                
                confidence = total_confidence / len(segments)
            
            # Prepare response
            transcription_result = {
                "success": True,
                "text": result.get("text", ""),
                "language": result.get("language", "unknown"),
                "segments": segments,
                "confidence": confidence,
                "processing_time": processing_time,
                "model_used": self.model_name,
                "file_path": str(audio_path),
                "task": task
            }
            
            print(f"Transcription completed in {processing_time:.2f} seconds")
            return transcription_result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Transcription failed: {str(e)}",
                "file_path": str(audio_path),
                "model_used": self.model_name
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model
        
        Returns:
            Dictionary with model information
        """
        if not self.model_loaded:
            return {"error": "No model loaded"}
        
        try:
            return {
                "model_name": self.model_name,
                "model_loaded": self.model_loaded,
                "model_size": f"{self.model.dims.n_text_state}M parameters" if hasattr(self.model, 'dims') else "Unknown",
                "available_models": config.AVAILABLE_MODELS
            }
        except Exception as e:
            return {
                "error": f"Error getting model info: {str(e)}",
                "model_name": self.model_name,
                "model_loaded": self.model_loaded
            }
    
    def detect_language(self, audio_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Detect the language of the audio file
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Dictionary with language detection results
        """
        if not self.model_loaded:
            if not self.load_model():
                return {"error": "Failed to load Whisper model"}
        
        try:
            audio_path = Path(audio_path)
            
            # Load and prepare audio
            audio = whisper.load_audio(str(audio_path))
            audio = whisper.pad_or_trim(audio)
            
            # Make log-Mel spectrogram
            mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
            
            # Detect language
            _, probs = self.model.detect_language(mel)
            detected_language = max(probs, key=probs.get)
            
            return {
                "success": True,
                "detected_language": detected_language,
                "language_probabilities": probs,
                "file_path": str(audio_path)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Language detection failed: {str(e)}",
                "file_path": str(audio_path)
            } 
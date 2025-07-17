"""
Audio and video file processing utilities for Whisper AI Transcription Project
"""

import os
import ffmpeg
from pathlib import Path
from typing import Union, Tuple, Optional
import config
import subprocess


class AudioProcessor:
    """Handles audio and video file processing for transcription"""
    
    def __init__(self):
        self.supported_audio_formats = config.SUPPORTED_AUDIO_FORMATS
        self.supported_video_formats = config.SUPPORTED_VIDEO_FORMATS
        self.max_file_size_mb = config.MAX_FILE_SIZE_MB
        # Set FFmpeg path - try to find it automatically
        self.ffmpeg_path = self._find_ffmpeg()
    
    def _find_ffmpeg(self) -> str:
        """Find FFmpeg executable path"""
        possible_paths = [
            "C:\\ffmpeg\\bin\\ffmpeg.exe",
            "ffmpeg",  # If it's in PATH
            "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe",
            "C:\\Program Files (x86)\\ffmpeg\\bin\\ffmpeg.exe",
        ]
        
        for path in possible_paths:
            try:
                result = subprocess.run([path, '-version'], capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ Found FFmpeg at: {path}")
                    return path
            except:
                continue
        
        print("⚠️ FFmpeg not found, using fallback duration detection")
        return "ffmpeg"  # Fallback
    
    def validate_file(self, file_path: Union[str, Path]) -> Tuple[bool, str]:
        """
        Validate if the file exists and is in a supported format
        
        Args:
            file_path: Path to the audio/video file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            file_path = Path(file_path)
            
            # Check if file exists
            if not file_path.exists():
                return False, f"File not found: {file_path}"
            
            # Check if it's a file
            if not file_path.is_file():
                return False, f"Path is not a file: {file_path}"
            
            # Check file extension
            file_extension = file_path.suffix.lower()
            if file_extension not in self.supported_audio_formats + self.supported_video_formats:
                return False, f"Unsupported file format: {file_extension}. Supported formats: {self.supported_audio_formats + self.supported_video_formats}"
            
            # Check file size
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            if file_size_mb > self.max_file_size_mb:
                return False, f"File too large: {file_size_mb:.1f}MB. Maximum allowed: {self.max_file_size_mb}MB"
            
            return True, "File is valid"
            
        except Exception as e:
            return False, f"Error validating file: {str(e)}"
    
    def get_file_info(self, file_path: Union[str, Path]) -> dict:
        """
        Get basic information about the audio/video file
        
        Args:
            file_path: Path to the audio/video file
            
        Returns:
            Dictionary with file information
        """
        file_path = Path(file_path)
        
        try:
            # Get basic file info
            file_info = {
                'path': str(file_path),
                'name': file_path.name,
                'extension': file_path.suffix.lower(),
                'size_mb': file_path.stat().st_size / (1024 * 1024),
                'is_audio': file_path.suffix.lower() in self.supported_audio_formats,
                'is_video': file_path.suffix.lower() in self.supported_video_formats
            }
            
            # Get audio/video metadata using ffmpeg
            try:
                # Use subprocess to call ffmpeg directly
                result = subprocess.run([
                    self.ffmpeg_path, '-i', str(file_path), '-f', 'null', '-'
                ], capture_output=True, text=True, stderr=subprocess.PIPE)
                
                # Parse duration from stderr output
                import re
                duration_match = re.search(r'Duration: (\d{2}):(\d{2}):(\d{2})\.(\d{2})', result.stderr)
                if duration_match:
                    hours, minutes, seconds, centiseconds = map(int, duration_match.groups())
                    file_info['duration'] = hours * 3600 + minutes * 60 + seconds + centiseconds / 100
                    print(f"✅ Extracted duration: {file_info['duration']}s")
                else:
                    # Try alternative duration format
                    duration_match = re.search(r'Duration: (\d{2}):(\d{2}):(\d{2})', result.stderr)
                    if duration_match:
                        hours, minutes, seconds = map(int, duration_match.groups())
                        file_info['duration'] = hours * 3600 + minutes * 60 + seconds
                        print(f"✅ Extracted duration (alt): {file_info['duration']}s")
                    else:
                        file_info['duration'] = 0
                        print(f"⚠️ Could not extract duration from: {result.stderr[:200]}...")
                
                # Get basic audio info
                file_info['sample_rate'] = 0  # Will be updated if we can parse it
                file_info['channels'] = 0
                file_info['codec'] = 'unknown'
                        
            except Exception as e:
                # If ffmpeg fails, still return basic info
                file_info['duration'] = 0
                file_info['sample_rate'] = 0
                file_info['channels'] = 0
                file_info['codec'] = 'unknown'
                print(f"⚠️ FFmpeg error: {e}")
            
            return file_info
            
        except Exception as e:
            return {
                'path': str(file_path),
                'error': str(e)
            }
    
    def extract_audio_from_video(self, video_path: Union[str, Path], output_path: Optional[Union[str, Path]] = None) -> Tuple[bool, str]:
        """
        Extract audio from video file for transcription
        
        Args:
            video_path: Path to the video file
            output_path: Path for the extracted audio (optional)
            
        Returns:
            Tuple of (success, message or output_path)
        """
        try:
            video_path = Path(video_path)
            
            # Validate video file
            is_valid, error_msg = self.validate_file(video_path)
            if not is_valid:
                return False, error_msg
            
            # Generate output path if not provided
            if output_path is None:
                output_path = video_path.parent / f"{video_path.stem}_audio.wav"
            else:
                output_path = Path(output_path)
            
            # Extract audio using ffmpeg via subprocess
            result = subprocess.run([
                self.ffmpeg_path, '-i', str(video_path), 
                '-acodec', 'pcm_s16le', '-ac', '1', '-ar', '16000',
                '-y', str(output_path)
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"FFmpeg error: {result.stderr}")
            
            return True, str(output_path)
            
        except Exception as e:
            return False, f"Error extracting audio: {str(e)}"
    
    def prepare_audio_for_whisper(self, file_path: Union[str, Path]) -> Tuple[bool, str]:
        """
        Prepare audio file for Whisper transcription
        
        Args:
            file_path: Path to the audio/video file
            
        Returns:
            Tuple of (success, prepared_audio_path)
        """
        try:
            file_path = Path(file_path)
            
            # Validate file
            is_valid, error_msg = self.validate_file(file_path)
            if not is_valid:
                return False, error_msg
            
            # If it's a video file, extract audio first
            if file_path.suffix.lower() in self.supported_video_formats:
                success, result = self.extract_audio_from_video(file_path)
                if not success:
                    return False, result
                file_path = Path(result)
            
            # For audio files, we can use them directly
            # Whisper will handle the audio processing internally
            return True, str(file_path)
            
        except Exception as e:
            return False, f"Error preparing audio: {str(e)}" 
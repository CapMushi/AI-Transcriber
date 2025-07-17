"""
Simple test script to debug Whisper audio loading
"""

import whisper
import os
from pathlib import Path

def test_whisper_loading():
    """Test if Whisper can load and transcribe the audio file"""
    
    file_path = "sample-0.mp3"
    
    print(f"Testing file: {file_path}")
    print(f"File exists: {os.path.exists(file_path)}")
    print(f"File size: {os.path.getsize(file_path)} bytes")
    print(f"Absolute path: {os.path.abspath(file_path)}")
    
    # Set FFmpeg path for Whisper
    os.environ["PATH"] = os.environ["PATH"] + ";C:\\ffmpeg\\bin"
    print(f"Updated PATH to include FFmpeg")
    
    try:
        # Load model
        print("Loading Whisper model...")
        model = whisper.load_model("base")
        print("Model loaded successfully")
        
        # Try to transcribe
        print("Attempting transcription...")
        result = model.transcribe(file_path)
        print("Transcription successful!")
        print(f"Text: {result['text']}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e)}")

if __name__ == "__main__":
    test_whisper_loading() 
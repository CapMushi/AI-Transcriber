"""
Test script to check duration extraction from uploaded files
"""

import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.append(os.path.dirname(__file__))

from src.audio_processor import AudioProcessor

def test_duration_extraction():
    """Test duration extraction from uploaded files"""
    
    # Initialize audio processor
    processor = AudioProcessor()
    
    # Check the temp upload directory
    temp_dir = "C:\\Users\\Admin\\AppData\\Local\\Temp\\whisper_uploads"
    upload_dir = Path(temp_dir)
    
    if not upload_dir.exists():
        print(f"❌ Upload directory not found: {temp_dir}")
        return
    
    print(f"📁 Checking upload directory: {temp_dir}")
    
    # List all files in the upload directory
    files = list(upload_dir.glob("*.mp3"))
    print(f"📂 Found {len(files)} MP3 files")
    
    for file_path in files:
        print(f"\n🔍 Testing file: {file_path.name}")
        
        # Test file validation
        is_valid, error_msg = processor.validate_file(file_path)
        print(f"   Validation: {'✅ Valid' if is_valid else f'❌ Invalid: {error_msg}'}")
        
        if is_valid:
            # Test file info extraction
            file_info = processor.get_file_info(file_path)
            print(f"   File info: {file_info}")
            
            # Test audio preparation
            success, result = processor.prepare_audio_for_whisper(file_path)
            print(f"   Audio preparation: {'✅ Success' if success else f'❌ Failed: {result}'}")

if __name__ == "__main__":
    test_duration_extraction() 
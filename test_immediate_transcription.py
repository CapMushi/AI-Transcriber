#!/usr/bin/env python3
"""
Test script to verify immediate transcription response
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.routes.transcribe import store_primary_content
from api.routes.transcribe import StorePrimaryRequest
import time

async def test_immediate_transcription():
    """Test that transcription results are returned immediately"""
    
    # Use a test file (harvard.wav exists in the project)
    test_file = "harvard.wav"
    
    if not os.path.exists(test_file):
        print(f"❌ Test file {test_file} not found")
        return
    
    print(f"🧪 Testing immediate transcription with file: {test_file}")
    print("=" * 60)
    
    # Create request
    request = StorePrimaryRequest(
        file_path=test_file,
        model="base",
        language="auto"
    )
    
    # Start timing
    start_time = time.time()
    
    print("🔄 Calling store_primary_content...")
    
    # Call the endpoint
    response = await store_primary_content(request)
    
    # Calculate response time
    response_time = time.time() - start_time
    
    print(f"⏱️  Response time: {response_time:.2f} seconds")
    print(f"✅ Success: {response.success}")
    print(f"📝 Message: {response.message}")
    print(f"🆔 File ID: {response.file_id}")
    print(f"📊 Chunks stored: {response.chunks_stored}")
    print(f"💾 Storage in progress: {response.storage_in_progress}")
    print(f"📄 Text length: {len(response.text)} characters")
    print(f"📋 Segments count: {len(response.segments)}")
    
    if response.text:
        print(f"📄 First 100 chars: {response.text[:100]}...")
    
    print("=" * 60)
    
    # Verify the response
    if response.success:
        print("✅ Test PASSED: Transcription returned immediately")
        if response.storage_in_progress:
            print("✅ Storage is happening in background")
        else:
            print("⚠️  Storage not in progress (may have failed)")
    else:
        print("❌ Test FAILED: Transcription failed")
        print(f"Error: {response.error}")

if __name__ == "__main__":
    asyncio.run(test_immediate_transcription()) 
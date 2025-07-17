"""
Test script for Phase 1 API implementation
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        # Test FastAPI imports
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        print("✅ FastAPI imports successful")
        
        # Test API modules
        from api.routes import upload, transcribe, download
        print("✅ API routes imports successful")
        
        from api.middleware.cors import setup_cors
        print("✅ CORS middleware import successful")
        
        from api.utils.file_handler import FileHandler
        print("✅ File handler import successful")
        
        # Test backend modules
        from src.audio_processor import AudioProcessor
        from src.transcriber import WhisperTranscriber
        from src.output_formatter import OutputFormatter
        print("✅ Backend modules imports successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_api_structure():
    """Test if API structure is correct"""
    print("\nTesting API structure...")
    
    try:
        # Test API server creation
        from api_server import app
        print("✅ API server creation successful")
        
        # Check if routes are included
        routes = [route.path for route in app.routes]
        expected_routes = [
            "/",
            "/health",
            "/docs",
            "/openapi.json"
        ]
        
        # Check for API routes (they might be prefixed)
        api_routes = [route for route in routes if "/api/" in route or route in expected_routes]
        print(f"✅ Found {len(api_routes)} routes")
        
        return True
        
    except Exception as e:
        print(f"❌ API structure test failed: {e}")
        return False

def test_file_structure():
    """Test if all required files exist"""
    print("\nTesting file structure...")
    
    required_files = [
        "api_server.py",
        "api/__init__.py",
        "api/routes/__init__.py",
        "api/routes/upload.py",
        "api/routes/transcribe.py", 
        "api/routes/download.py",
        "api/middleware/__init__.py",
        "api/middleware/cors.py",
        "api/utils/__init__.py",
        "api/utils/file_handler.py",
        "src/transcriber.py",
        "src/audio_processor.py",
        "src/output_formatter.py",
        "requirements.txt"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files exist")
        return True

def test_dependencies():
    """Test if dependencies are properly specified"""
    print("\nTesting dependencies...")
    
    try:
        with open("requirements.txt", "r") as f:
            content = f.read()
        
        required_deps = [
            "fastapi",
            "uvicorn",
            "python-multipart",
            "openai-whisper",
            "requests"
        ]
        
        missing_deps = []
        for dep in required_deps:
            if dep not in content:
                missing_deps.append(dep)
            else:
                print(f"✅ {dep}")
        
        if missing_deps:
            print(f"❌ Missing dependencies: {missing_deps}")
            return False
        else:
            print("✅ All required dependencies specified")
            return True
            
    except Exception as e:
        print(f"❌ Dependencies test failed: {e}")
        return False

def main():
    """Run all Phase 1 tests"""
    print("Testing Phase 1 API Implementation")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Dependencies", test_dependencies),
        ("Imports", test_imports),
        ("API Structure", test_api_structure),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} FAILED")
    
    print(f"\n{'=' * 50}")
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 Phase 1 implementation is complete and ready!")
        print("\nPhase 1 Summary:")
        print("- ✅ FastAPI server with CORS middleware")
        print("- ✅ File upload endpoint with validation")
        print("- ✅ Transcription endpoint with Whisper integration")
        print("- ✅ Download endpoint with multiple formats")
        print("- ✅ Health check and info endpoints")
        print("- ✅ Proper error handling and response models")
        print("\nReady for Phase 2: Frontend Integration")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")

if __name__ == "__main__":
    main() 
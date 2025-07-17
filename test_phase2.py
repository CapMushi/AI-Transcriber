"""
Test script for Phase 2 Frontend Integration
Tests the API endpoints that the frontend will use
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health check endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health check: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_supported_formats():
    """Test supported formats endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/supported-formats")
        print(f"✅ Supported formats: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Audio formats: {data.get('audio_formats', [])}")
            print(f"   Video formats: {data.get('video_formats', [])}")
            print(f"   Max file size: {data.get('max_file_size_mb', 0)}MB")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Supported formats failed: {e}")
        return False

def test_available_models():
    """Test available models endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/models")
        print(f"✅ Available models: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Models: {data.get('available_models', [])}")
            print(f"   Default: {data.get('default_model', '')}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Available models failed: {e}")
        return False

def test_download_formats():
    """Test download formats endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/formats")
        print(f"✅ Download formats: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Formats: {data.get('available_formats', [])}")
            print(f"   Default: {data.get('default_format', '')}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Download formats failed: {e}")
        return False

def test_api_info():
    """Test API info endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ API info: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Message: {data.get('message', '')}")
            print(f"   Version: {data.get('version', '')}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ API info failed: {e}")
        return False

def test_cors_headers():
    """Test CORS headers are present"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        cors_headers = [
            'Access-Control-Allow-Origin',
            'Access-Control-Allow-Methods',
            'Access-Control-Allow-Headers'
        ]
        
        print(f"✅ CORS headers check:")
        for header in cors_headers:
            if header in response.headers:
                print(f"   ✅ {header}: {response.headers[header]}")
            else:
                print(f"   ❌ {header}: Missing")
        
        return all(header in response.headers for header in cors_headers)
    except Exception as e:
        print(f"❌ CORS headers check failed: {e}")
        return False

def main():
    """Run all Phase 2 tests"""
    print("Testing Phase 2 Frontend Integration")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_check),
        ("API Info", test_api_info),
        ("Supported Formats", test_supported_formats),
        ("Available Models", test_available_models),
        ("Download Formats", test_download_formats),
        ("CORS Headers", test_cors_headers),
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
        print("🎉 Phase 2 API endpoints are ready for frontend integration!")
        print("\nPhase 2 Summary:")
        print("- ✅ Health check endpoint working")
        print("- ✅ API info endpoint working")
        print("- ✅ Supported formats endpoint working")
        print("- ✅ Available models endpoint working")
        print("- ✅ Download formats endpoint working")
        print("- ✅ CORS headers configured")
        print("\nFrontend can now:")
        print("- Upload files to /api/upload")
        print("- Transcribe files via /api/transcribe")
        print("- Download results via /api/download")
        print("- Get configuration from various endpoints")
    else:
        print("⚠️  Some tests failed. Check the API server.")

if __name__ == "__main__":
    main() 
"""
Test script for Whisper AI API
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health check: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_root():
    """Test root endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Root endpoint: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Root endpoint failed: {e}")
        return False

def test_supported_formats():
    """Test supported formats endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/supported-formats")
        print(f"Supported formats: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Supported formats failed: {e}")
        return False

def test_models():
    """Test models endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/models")
        print(f"Models: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Models failed: {e}")
        return False

def test_download_formats():
    """Test download formats endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/formats")
        print(f"Download formats: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Download formats failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Whisper AI API...")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health),
        ("Root Endpoint", test_root),
        ("Supported Formats", test_supported_formats),
        ("Available Models", test_models),
        ("Download Formats", test_download_formats),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            print("✅ PASSED")
            passed += 1
        else:
            print("❌ FAILED")
    
    print(f"\n{'=' * 50}")
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! API is ready for frontend integration.")
    else:
        print("⚠️  Some tests failed. Check the API server.") 
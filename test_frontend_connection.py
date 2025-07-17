"""
Test script to verify API server is running and accessible
"""

import requests
import time

def test_api_connection():
    """Test if API server is running and accessible"""
    base_url = "http://localhost:8000"
    
    print("Testing API server connection...")
    print("=" * 40)
    
    # Test health endpoint
    try:
        print("1. Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        print("   ✅ Health endpoint working")
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to API server")
        print("   Make sure to run: python api_server.py")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test API info endpoint
    try:
        print("\n2. Testing API info endpoint...")
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        print("   ✅ API info endpoint working")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test supported formats endpoint
    try:
        print("\n3. Testing supported formats endpoint...")
        response = requests.get(f"{base_url}/api/supported-formats", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        print("   ✅ Supported formats endpoint working")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test CORS headers
    try:
        print("\n4. Testing CORS headers...")
        response = requests.get(f"{base_url}/health", timeout=5)
        cors_headers = ['Access-Control-Allow-Origin', 'Access-Control-Allow-Methods']
        for header in cors_headers:
            if header in response.headers:
                print(f"   ✅ {header}: {response.headers[header]}")
            else:
                print(f"   ❌ {header}: Missing")
        print("   ✅ CORS headers check complete")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print("\n" + "=" * 40)
    print("✅ API server is running and accessible!")
    print("Frontend should be able to connect to the API.")
    return True

if __name__ == "__main__":
    test_api_connection() 
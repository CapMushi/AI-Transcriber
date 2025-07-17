"""
Test CORS headers specifically
"""

import requests

def test_cors_headers():
    """Test CORS headers on the API server"""
    try:
        print("Testing CORS headers...")
        
        # Test OPTIONS request (preflight)
        response = requests.options("http://localhost:8000/health")
        print(f"OPTIONS request status: {response.status_code}")
        print("CORS headers:")
        for header, value in response.headers.items():
            if 'access-control' in header.lower():
                print(f"  {header}: {value}")
        
        # Test GET request
        response = requests.get("http://localhost:8000/health")
        print(f"\nGET request status: {response.status_code}")
        print("CORS headers:")
        for header, value in response.headers.items():
            if 'access-control' in header.lower():
                print(f"  {header}: {value}")
        
        if 'access-control-allow-origin' in response.headers:
            print("✅ CORS headers are present!")
        else:
            print("❌ CORS headers are missing!")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_cors_headers() 
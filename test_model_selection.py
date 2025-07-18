"""
Test script to verify model selection is working
"""

import requests
import json

def test_model_selection():
    """Test that different models are actually used"""
    
    # Test different models
    models_to_test = ['tiny', 'base', 'small']
    
    for model in models_to_test:
        print(f"\n🧪 Testing model: {model}")
        
        try:
            response = requests.post('http://localhost:8000/api/transcribe', 
                                  json={
                                      'file_path': 'testing files/sample-0.mp3',
                                      'model': model
                                  })
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Model used: {result.get('model_used')}")
                print(f"✅ Success: {result.get('success')}")
                print(f"✅ Processing time: {result.get('processing_time', 0):.2f}s")
                
                # Verify the model actually changed
                if result.get('model_used') == model:
                    print(f"✅ Model selection working correctly!")
                else:
                    print(f"❌ Model selection failed! Expected: {model}, Got: {result.get('model_used')}")
            else:
                print(f"❌ API request failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing model {model}: {e}")

if __name__ == "__main__":
    print("🚀 Testing Model Selection Implementation")
    print("=" * 50)
    test_model_selection()
    print("\n✅ Model selection test completed!") 
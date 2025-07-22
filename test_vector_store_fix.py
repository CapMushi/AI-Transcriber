"""
Test script to verify vector store methods are working
"""

import sys
import os
from pathlib import Path

# Add the project root to the path
sys.path.append(str(Path(__file__).parent))

def test_vector_store_methods():
    """Test that the missing methods are now available"""
    print("🔧 Testing vector store methods...")
    
    try:
        from src.vector_store import PineconeVectorStore
        
        # Test vector store initialization
        vector_store = PineconeVectorStore()
        print("✅ Vector store initialized")
        
        # Test clear method exists
        if hasattr(vector_store, 'clear_existing_embeddings'):
            print("✅ clear_existing_embeddings method available")
        else:
            print("❌ clear_existing_embeddings method not found")
            return False
        
        # Test search method exists
        if hasattr(vector_store, 'search_content_matches'):
            print("✅ search_content_matches method available")
        else:
            print("❌ search_content_matches method not found")
            return False
        
        # Test merge method exists
        if hasattr(vector_store, '_merge_overlapping_matches'):
            print("✅ _merge_overlapping_matches method available")
        else:
            print("❌ _merge_overlapping_matches method not found")
            return False
        
        print("✅ All required methods are available!")
        return True
        
    except Exception as e:
        print(f"❌ Vector store test failed: {e}")
        return False

def test_vector_handler():
    """Test that vector handler can use the new methods"""
    print("\n🔧 Testing vector handler...")
    
    try:
        from api.utils.vector_handler import VectorHandler
        
        # Test vector handler initialization
        vector_handler = VectorHandler()
        print("✅ Vector handler initialized")
        
        # Test that it can access the vector store methods
        if hasattr(vector_handler.vector_store, 'clear_existing_embeddings'):
            print("✅ Vector handler can access clear_existing_embeddings")
        else:
            print("❌ Vector handler cannot access clear_existing_embeddings")
            return False
        
        if hasattr(vector_handler.vector_store, 'search_content_matches'):
            print("✅ Vector handler can access search_content_matches")
        else:
            print("❌ Vector handler cannot access search_content_matches")
            return False
        
        print("✅ Vector handler can access all required methods!")
        return True
        
    except Exception as e:
        print(f"❌ Vector handler test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Vector Store Fix Verification")
    print("=" * 40)
    
    tests = [
        ("Vector Store Methods", test_vector_store_methods),
        ("Vector Handler", test_vector_handler),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ Vector store fix is complete!")
        print("\n🎉 The missing methods have been added:")
        print("✅ clear_existing_embeddings")
        print("✅ search_content_matches")
        print("✅ _merge_overlapping_matches")
        print("\n🚀 Ready to test the frontend!")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    main() 
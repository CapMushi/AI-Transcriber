"""
Test script for Phase 1 Pinecone integration
"""

import sys
import os
from pathlib import Path

# Add the project root to the path
sys.path.append(str(Path(__file__).parent))

def test_configuration():
    """Test configuration loading"""
    print("🔧 Testing configuration...")
    
    try:
        import config
        
        # Test basic config
        print(f"✅ Default model: {config.DEFAULT_MODEL}")
        print(f"✅ Available models: {config.AVAILABLE_MODELS}")
        
        # Test Pinecone config
        print(f"✅ Pinecone API key configured: {bool(config.PINECONE_API_KEY)}")
        print(f"✅ Pinecone environment: {config.PINECONE_ENVIRONMENT}")
        print(f"✅ Pinecone index name: {config.PINECONE_INDEX_NAME}")
        
        # Test OpenAI config
        print(f"✅ OpenAI API key configured: {bool(config.OPENAI_API_KEY)}")
        
        # Test chunking config
        print(f"✅ Chunking config: {config.CHUNKING_CONFIG}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_imports():
    """Test module imports"""
    print("\n📦 Testing imports...")
    
    try:
        # Test vector store
        from src.vector_store import PineconeVectorStore
        print("✅ PineconeVectorStore imported successfully")
        
        # Test vector handler
        from api.utils.vector_handler import VectorHandler
        print("✅ VectorHandler imported successfully")
        
        # Test chunking utils
        from src.chunking_utils import ChunkingUtils
        print("✅ ChunkingUtils imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def test_vector_store_initialization():
    """Test vector store initialization"""
    print("\n🏪 Testing vector store initialization...")
    
    try:
        from src.vector_store import PineconeVectorStore
        
        vector_store = PineconeVectorStore()
        
        # Test configuration validation
        is_valid = vector_store.validate_configuration()
        print(f"✅ Configuration valid: {is_valid}")
        
        # Test status
        print(f"✅ API key present: {bool(vector_store.api_key)}")
        print(f"✅ OpenAI client available: {bool(vector_store.openai_client)}")
        print(f"✅ Index name: {vector_store.index_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Vector store initialization failed: {e}")
        return False

def test_chunking_utils():
    """Test chunking utilities"""
    print("\n✂️ Testing chunking utilities...")
    
    try:
        from src.chunking_utils import ChunkingUtils
        import config
        
        # Test configuration validation
        is_valid, message = ChunkingUtils.validate_chunking_config(config.CHUNKING_CONFIG)
        print(f"✅ Chunking config valid: {is_valid}")
        if not is_valid:
            print(f"❌ Config error: {message}")
        
        # Test with sample transcription data
        sample_transcription = {
            "success": True,
            "text": "Hello world. This is a test transcription with multiple sentences.",
            "segments": [
                {"start": 0.0, "end": 2.0, "text": "Hello world."},
                {"start": 2.0, "end": 5.0, "text": "This is a test transcription with multiple sentences."}
            ],
            "language": "en",
            "model_used": "base",
            "confidence": 95.0,
            "processing_time": 2.5
        }
        
        chunks = ChunkingUtils.chunk_transcription(sample_transcription)
        print(f"✅ Generated {len(chunks)} chunks from sample transcription")
        
        for i, chunk in enumerate(chunks):
            print(f"  Chunk {i+1}: {chunk['text'][:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Chunking utils test failed: {e}")
        return False

def test_vector_handler():
    """Test vector handler"""
    print("\n🔧 Testing vector handler...")
    
    try:
        from api.utils.vector_handler import VectorHandler
        
        handler = VectorHandler()
        
        # Test file ID generation
        file_id = handler.generate_file_id()
        print(f"✅ Generated file ID: {file_id}")
        
        # Test storage status
        status = handler.get_storage_status()
        print(f"✅ Storage status: {status}")
        
        # Test metadata preparation
        sample_file_info = {
            "size_mb": 2.5,
            "duration": 30.0,
            "extension": ".mp3",
            "is_audio": True,
            "is_video": False
        }
        
        metadata = handler.prepare_file_metadata("test.mp3", sample_file_info)
        print(f"✅ Prepared metadata: {metadata}")
        
        return True
        
    except Exception as e:
        print(f"❌ Vector handler test failed: {e}")
        return False

def main():
    """Run all Phase 1 tests"""
    print("🚀 Phase 1 Pinecone Integration Tests")
    print("=" * 50)
    
    tests = [
        test_configuration,
        test_imports,
        test_vector_store_initialization,
        test_chunking_utils,
        test_vector_handler
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ Phase 1 implementation is ready!")
        print("\n📝 Next steps:")
        print("1. Set up your .env file with API keys")
        print("2. Run Phase 2 implementation")
        print("3. Test with actual transcription data")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    main() 
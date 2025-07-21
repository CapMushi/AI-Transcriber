"""
Pinecone vector storage for transcription chunks
"""

import pinecone
import openai
import uuid
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import config


class PineconeVectorStore:
    """Handles Pinecone vector storage operations for transcription chunks"""
    
    def __init__(self):
        """Initialize Pinecone client and validate configuration"""
        self.api_key = config.PINECONE_API_KEY
        self.environment = config.PINECONE_ENVIRONMENT
        self.index_name = config.PINECONE_INDEX_NAME
        self.client = None
        self.index = None
        self.openai_client = None
        
        # Initialize OpenAI client for embeddings
        if config.OPENAI_API_KEY:
            openai.api_key = config.OPENAI_API_KEY
            self.openai_client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        
        # Initialize Pinecone client
        if self.api_key:
            try:
                self.client = pinecone.Pinecone(api_key=self.api_key)
                print(f"✅ Pinecone initialized for index: {self.index_name}")
            except Exception as e:
                print(f"❌ Pinecone initialization failed: {e}")
                self.client = None
    
    def validate_configuration(self) -> bool:
        """
        Validate that all required configuration is present
        
        Returns:
            True if configuration is valid, False otherwise
        """
        if not self.api_key:
            print("⚠️ Pinecone API key not found")
            return False
        
        if not config.OPENAI_API_KEY:
            print("⚠️ OpenAI API key not found")
            return False
        
        if not self.client:
            print("⚠️ Pinecone client not initialized")
            return False
        
        return True
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        """
        Get embedding for text using OpenAI API
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector or None if failed
        """
        if not self.openai_client:
            print("❌ OpenAI client not available")
            return None
        
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"❌ Embedding generation failed: {e}")
            return None
    
    def store_transcription_chunks(self, 
                                 file_id: str,
                                 transcription_data: Dict[str, Any],
                                 file_metadata: Dict[str, Any]) -> bool:
        """
        Store transcription chunks in Pinecone
        
        Args:
            file_id: Unique identifier for the file
            transcription_data: Transcription result from Whisper
            file_metadata: File information metadata
            
        Returns:
            True if storage successful, False otherwise
        """
        if not self.validate_configuration():
            return False
        
        try:
            # Get or create index
            if self.index_name not in self.client.list_indexes().names():
                print(f"❌ Index '{self.index_name}' not found")
                return False
            
            self.index = self.client.Index(self.index_name)
            
            # Generate chunks from transcription
            chunks = self._generate_chunks(transcription_data, file_metadata)
            
            if not chunks:
                print("⚠️ No chunks generated from transcription")
                return False
            
            # Store chunks in Pinecone
            vectors_to_upsert = []
            
            for chunk in chunks:
                # Generate embedding
                embedding = self.get_embedding(chunk["text"])
                if not embedding:
                    continue
                
                # Create vector record
                vector_record = {
                    "id": chunk["id"],
                    "values": embedding,
                    "metadata": chunk["metadata"]
                }
                vectors_to_upsert.append(vector_record)
            
            if vectors_to_upsert:
                # Upsert in batches
                batch_size = 100
                for i in range(0, len(vectors_to_upsert), batch_size):
                    batch = vectors_to_upsert[i:i + batch_size]
                    self.index.upsert(vectors=batch)
                
                print(f"✅ Stored {len(vectors_to_upsert)} chunks in Pinecone")
                return True
            else:
                print("⚠️ No valid vectors to store")
                return False
                
        except Exception as e:
            print(f"❌ Pinecone storage failed: {e}")
            return False
    
    def _generate_chunks(self, 
                        transcription_data: Dict[str, Any],
                        file_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate intelligent chunks from transcription data
        
        Args:
            transcription_data: Transcription result from Whisper
            file_metadata: File information metadata
            
        Returns:
            List of chunk dictionaries with metadata
        """
        chunks = []
        segments = transcription_data.get("segments", [])
        
        # Use Whisper segments as primary chunks
        for segment_index, segment in enumerate(segments):
            text = segment.get("text", "").strip()
            if not text:
                continue
            
            start_time = segment.get("start", 0)
            end_time = segment.get("end", 0)
            
            # Check if segment is too long and needs splitting
            if len(text) > config.CHUNKING_CONFIG["max_segment_length"]:
                # Split long segments
                sub_chunks = self._split_long_segment(
                    text, start_time, end_time, segment_index
                )
                chunks.extend(sub_chunks)
            else:
                # Use segment as-is
                chunk = self._create_chunk(
                    text, start_time, end_time, segment_index,
                    "segment", transcription_data, file_metadata
                )
                chunks.append(chunk)
        
        return chunks
    
    def _split_long_segment(self, 
                           text: str,
                           start_time: float,
                           end_time: float,
                           segment_index: int) -> List[Dict[str, Any]]:
        """
        Split a long segment into smaller chunks
        
        Args:
            text: Segment text
            start_time: Start timestamp
            end_time: End timestamp
            segment_index: Original segment index
            
        Returns:
            List of chunk dictionaries
        """
        chunks = []
        words = text.split()
        total_words = len(words)
        duration = end_time - start_time
        
        # Calculate words per second for time distribution
        words_per_second = total_words / duration if duration > 0 else 1
        
        # Split into chunks
        chunk_size = config.CHUNKING_CONFIG["max_chunk_size"]
        overlap_size = config.CHUNKING_CONFIG["overlap_size"]
        
        current_pos = 0
        chunk_index = 0
        
        while current_pos < total_words:
            # Calculate chunk boundaries
            end_pos = min(current_pos + chunk_size, total_words)
            
            # Extract chunk text
            chunk_words = words[current_pos:end_pos]
            chunk_text = " ".join(chunk_words)
            
            # Calculate chunk timestamps
            chunk_start = start_time + (current_pos / words_per_second)
            chunk_end = start_time + (end_pos / words_per_second)
            
            # Create chunk
            chunk = self._create_chunk(
                chunk_text, chunk_start, chunk_end, segment_index,
                "text_chunk", {}, {},  # Empty dicts for transcription_data and file_metadata
                chunk_index=chunk_index
            )
            chunks.append(chunk)
            
            # Move to next chunk with overlap
            current_pos = end_pos - overlap_size
            chunk_index += 1
            
            # Prevent infinite loop
            if current_pos >= total_words:
                break
        
        return chunks
    
    def _create_chunk(self,
                     text: str,
                     start_time: float,
                     end_time: float,
                     segment_index: int,
                     chunk_type: str,
                     transcription_data: Dict[str, Any],
                     file_metadata: Dict[str, Any],
                     chunk_index: int = 0) -> Dict[str, Any]:
        """
        Create a chunk with metadata
        
        Args:
            text: Chunk text
            start_time: Start timestamp
            end_time: End timestamp
            segment_index: Original segment index
            chunk_type: Type of chunk (segment or text_chunk)
            transcription_data: Transcription result
            file_metadata: File metadata
            chunk_index: Chunk index within segment
            
        Returns:
            Chunk dictionary
        """
        # Generate unique ID
        chunk_id = f"{uuid.uuid4()}"
        
        # Create metadata
        metadata = {
            "text": text,
            "start_time": start_time,
            "end_time": end_time,
            "segment_index": segment_index,
            "chunk_type": chunk_type,
            "chunk_index": chunk_index,
            "language": transcription_data.get("language", "unknown"),
            "model_used": transcription_data.get("model_used", "unknown"),
            "confidence": transcription_data.get("confidence", 0.0),
            "original_filename": file_metadata.get("original_name", "unknown"),
            "file_size_mb": file_metadata.get("size_mb", 0),
            "duration": file_metadata.get("duration", 0),
            "upload_date": datetime.now().isoformat(),
            "file_type": file_metadata.get("extension", ""),
            "is_audio": file_metadata.get("is_audio", False),
            "is_video": file_metadata.get("is_video", False)
        }
        
        return {
            "id": chunk_id,
            "text": text,
            "metadata": metadata
        }
    
    def search_chunks(self, 
                     query: str,
                     top_k: int = 5,
                     filter_metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Search for chunks in Pinecone
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Metadata filters
            
        Returns:
            List of search results
        """
        if not self.validate_configuration():
            return []
        
        try:
            # Get embedding for query
            query_embedding = self.get_embedding(query)
            if not query_embedding:
                return []
            
            # Search in Pinecone
            self.index = self.client.Index(self.index_name)
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_metadata
            )
            
            return results.matches
            
        except Exception as e:
            print(f"❌ Pinecone search failed: {e}")
            return [] 
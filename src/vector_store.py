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
    
    def get_embeddings_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Get embeddings for multiple texts in a single API call
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors (None for failed embeddings)
        """
        if not self.openai_client:
            print("❌ OpenAI client not available")
            return [None] * len(texts)
        
        if not texts:
            return []
        
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=texts
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            print(f"❌ Batch embedding generation failed: {e}")
            return [None] * len(texts)
    
    def clear_existing_embeddings(self) -> bool:
        """
        Clear all existing embeddings from Pinecone index
        
        Returns:
            True if clear successful, False otherwise
        """
        if not self.validate_configuration():
            return False
        
        try:
            # Get index
            if self.index_name not in self.client.list_indexes().names():
                print(f"❌ Index '{self.index_name}' not found")
                return False
            
            self.index = self.client.Index(self.index_name)
            
            # Delete all vectors from the index
            self.index.delete(delete_all=True)
            
            print(f"✅ Cleared all embeddings from index: {self.index_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to clear embeddings: {e}")
            return False
    
    def search_content_matches(self,
                             secondary_transcription: Dict[str, Any],
                             threshold: float = 0.95) -> Dict[str, Any]:
        """
        Search for secondary content matches in primary content using partial matching
        
        Args:
            secondary_transcription: Transcription result from secondary file
            threshold: Confidence threshold for matches (0.0 to 1.0)
            
        Returns:
            Dictionary with search results including matches and timestamps
        """
        print(f"🔍 DEBUG: search_content_matches called with threshold={threshold}")
        
        if not self.validate_configuration():
            print("❌ DEBUG: Configuration validation failed")
            return {
                "success": False,
                "error": "Configuration validation failed",
                "matches": [],
                "confidence": 0.0
            }
        
        try:
            # Get secondary text
            secondary_text = secondary_transcription.get("text", "").strip()
            if not secondary_text:
                print("❌ DEBUG: No text found in secondary transcription")
                return {
                    "success": False,
                    "error": "No text found in secondary transcription",
                    "matches": [],
                    "confidence": 0.0
                }
            print(f"🔍 DEBUG: Secondary text: '{secondary_text}'")

            # Option 3: Dynamic threshold based on content length
            secondary_length = len(secondary_text)
            if secondary_length < 100:  # Short content
                adjusted_threshold = 0.5  # Lower threshold for short content
                print(f"📏 DEBUG: Short secondary content ({secondary_length} chars), using lower threshold: {adjusted_threshold}")
            elif secondary_length > 500:  # Very long content
                adjusted_threshold = 0.3  # Much lower threshold for very long content
                print(f"📏 DEBUG: Very long secondary content ({secondary_length} chars), using much lower threshold: {adjusted_threshold}")
            else:  # Medium content
                adjusted_threshold = threshold  # Use original threshold
                print(f"📏 DEBUG: Using original threshold: {adjusted_threshold}")

            # --- NEW: Chunk the secondary text ---
            secondary_chunks = self._chunk_secondary_text(secondary_transcription)
            print(f"🔍 DEBUG: Chunked secondary into {len(secondary_chunks)} chunks")

            # Extract chunk texts for batch embedding generation
            chunk_texts = []
            valid_chunks = []
            for chunk in secondary_chunks:
                chunk_text = chunk.get("text", "").strip()
                if chunk_text:
                    chunk_texts.append(chunk_text)
                    valid_chunks.append(chunk)

            if not chunk_texts:
                print("❌ DEBUG: No valid chunk texts found")
                return {
                    "success": False,
                    "error": "No valid chunk texts found",
                    "matches": [],
                    "confidence": 0.0
                }

            # Generate embeddings for all chunks in batch
            print(f"🔍 DEBUG: Generating batch embeddings for {len(chunk_texts)} chunks")
            batch_embeddings = self.get_embeddings_batch(chunk_texts)
            
            if not batch_embeddings or all(emb is None for emb in batch_embeddings):
                print("❌ DEBUG: Failed to generate batch embeddings")
                return {
                    "success": False,
                    "error": "Failed to generate batch embeddings",
                    "matches": [],
                    "confidence": 0.0
                }

            all_matches = []
            total_confidence = 0.0
            
            # Process each chunk with its pre-generated embedding
            for chunk_idx, (chunk, chunk_text, embedding) in enumerate(zip(valid_chunks, chunk_texts, batch_embeddings)):
                if not embedding:
                    print(f"❌ DEBUG: No embedding for chunk {chunk_idx+1}")
                    continue
                    
                print(f"🔍 DEBUG: Searching chunk {chunk_idx+1}/{len(valid_chunks)}: '{chunk_text[:50]}...'")
                chunk_matches = self._search_with_embedding(embedding, adjusted_threshold)
                
                for match in chunk_matches:
                    confidence = getattr(match, 'score', 0.0)
                    metadata = getattr(match, 'metadata', {})
                    match_text = metadata.get("text", "")
                    # Check both semantic similarity AND content overlap
                    has_content_overlap = self._check_content_overlap(chunk_text, match_text)
                    print(f"🔍 DEBUG: Chunk {chunk_idx+1} match - Confidence: {confidence:.3f}, Overlap: {has_content_overlap}")
                    if has_content_overlap:
                        all_matches.append({
                            "start_time": metadata.get("start_time", 0.0),
                            "end_time": metadata.get("end_time", 0.0),
                            "text": match_text,
                            "confidence": confidence,
                            "segment_index": metadata.get("segment_index", 0)
                        })
                        total_confidence += confidence
                        print(f"✅ DEBUG: Chunk {chunk_idx+1} match added to results")
                    else:
                        print(f"❌ DEBUG: Chunk {chunk_idx+1} match rejected (no content overlap)")

            print(f"🔍 DEBUG: {len(all_matches)} total matches above threshold AND with content overlap from all chunks")
            # Merge overlapping matches
            merged_matches = self._merge_overlapping_matches(all_matches)
            print(f"🔍 DEBUG: After merging: {len(merged_matches)} unique matches")
            avg_confidence = total_confidence / len(all_matches) if all_matches else 0.0
            result = {
                "success": True,
                "matches": merged_matches,
                "confidence": avg_confidence,
                "found": len(merged_matches) > 0,
                "total_matches": len(merged_matches),
                "search_text": secondary_text,
                "adjusted_threshold": adjusted_threshold
            }
            print(f"🔍 DEBUG: Final result: {result}")
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Content search failed: {str(e)}",
                "matches": [],
                "confidence": 0.0
            }
    
    def search_content_matches_optimized(self,
                                       secondary_transcription: Dict[str, Any],
                                       threshold: float = 0.95) -> Dict[str, Any]:
        """
        OPTIMIZED: Search for secondary content matches using batch Pinecone queries
        
        Args:
            secondary_transcription: Transcription result from secondary file
            threshold: Confidence threshold for matches (0.0 to 1.0)
            
        Returns:
            Dictionary with search results including matches and timestamps
        """
        print(f"🔍 DEBUG: OPTIMIZED search_content_matches called with threshold={threshold}")
        
        if not self.validate_configuration():
            print("❌ DEBUG: Configuration validation failed")
            return {
                "success": False,
                "error": "Configuration validation failed",
                "matches": [],
                "confidence": 0.0
            }
        
        try:
            # Get secondary text
            secondary_text = secondary_transcription.get("text", "").strip()
            if not secondary_text:
                print("❌ DEBUG: No text found in secondary transcription")
                return {
                    "success": False,
                    "error": "No text found in secondary transcription",
                    "matches": [],
                    "confidence": 0.0
                }
            print(f"🔍 DEBUG: Secondary text: '{secondary_text}'")

            # Dynamic threshold based on content length
            secondary_length = len(secondary_text)
            if secondary_length < 100:  # Short content
                adjusted_threshold = 0.5  # Lower threshold for short content
                print(f"📏 DEBUG: Short secondary content ({secondary_length} chars), using lower threshold: {adjusted_threshold}")
            elif secondary_length > 500:  # Very long content
                adjusted_threshold = 0.3  # Much lower threshold for very long content
                print(f"📏 DEBUG: Very long secondary content ({secondary_length} chars), using much lower threshold: {adjusted_threshold}")
            else:  # Medium content
                adjusted_threshold = threshold  # Use original threshold
                print(f"📏 DEBUG: Using original threshold: {adjusted_threshold}")

            # Chunk the secondary text
            secondary_chunks = self._chunk_secondary_text(secondary_transcription)
            print(f"🔍 DEBUG: Chunked secondary into {len(secondary_chunks)} chunks")

            # Extract chunk texts for batch embedding generation
            chunk_texts = []
            valid_chunks = []
            for chunk in secondary_chunks:
                chunk_text = chunk.get("text", "").strip()
                if chunk_text:
                    chunk_texts.append(chunk_text)
                    valid_chunks.append(chunk)

            if not chunk_texts:
                print("❌ DEBUG: No valid chunk texts found")
                return {
                    "success": False,
                    "error": "No valid chunk texts found",
                    "matches": [],
                    "confidence": 0.0
                }

            # Generate embeddings for all chunks in batch (already optimized)
            print(f"🔍 DEBUG: Generating batch embeddings for {len(chunk_texts)} chunks")
            batch_embeddings = self.get_embeddings_batch(chunk_texts)
            
            if not batch_embeddings or all(emb is None for emb in batch_embeddings):
                print("❌ DEBUG: Failed to generate batch embeddings")
                return {
                    "success": False,
                    "error": "Failed to generate batch embeddings",
                    "matches": [],
                    "confidence": 0.0
                }

            # OPTIMIZATION: Parallel individual queries instead of sequential
            if self.index and batch_embeddings:
                try:
                    print(f"🔍 DEBUG: OPTIMIZED: Running {len(batch_embeddings)} queries in parallel")
                    import concurrent.futures
                    from concurrent.futures import ThreadPoolExecutor

                    all_matches = []
                    total_confidence = 0.0

                    def process_chunk(args):
                        chunk_idx, chunk_text, embedding = args
                        if not embedding:
                            print(f"❌ DEBUG: No embedding for chunk {chunk_idx+1}")
                            return []
                        print(f"🔍 DEBUG: Processing chunk {chunk_idx+1}/{len(chunk_texts)}: '{chunk_text[:50]}...'")
                        chunk_matches = self._search_with_embedding(embedding, adjusted_threshold)
                        chunk_results = []
                        for match in chunk_matches:
                            confidence = getattr(match, 'score', 0.0)
                            metadata = getattr(match, 'metadata', {})
                            match_text = metadata.get("text", "")
                            has_content_overlap = self._check_content_overlap(chunk_text, match_text)
                            print(f"🔍 DEBUG: Chunk {chunk_idx+1} match - Confidence: {confidence:.3f}, Overlap: {has_content_overlap}")
                            if has_content_overlap:
                                chunk_results.append({
                                    "start_time": metadata.get("start_time", 0.0),
                                    "end_time": metadata.get("end_time", 0.0),
                                    "text": match_text,
                                    "confidence": confidence,
                                    "segment_index": metadata.get("segment_index", 0)
                                })
                                print(f"✅ DEBUG: Chunk {chunk_idx+1} match added to results")
                            else:
                                print(f"❌ DEBUG: Chunk {chunk_idx+1} match rejected (no content overlap)")
                        return chunk_results

                    chunk_args = [(i, chunk_texts[i], batch_embeddings[i]) for i in range(len(chunk_texts))]
                    with ThreadPoolExecutor(max_workers=min(8, len(chunk_args))) as executor:
                        results = list(executor.map(process_chunk, chunk_args))
                        for chunk_result in results:
                            all_matches.extend(chunk_result)
                            total_confidence += sum(match["confidence"] for match in chunk_result)

                    print(f"🔍 DEBUG: OPTIMIZED: {len(all_matches)} total matches from parallel queries")

                    # Merge overlapping matches (same logic as original)
                    merged_matches = self._merge_overlapping_matches(all_matches)
                    print(f"🔍 DEBUG: After merging: {len(merged_matches)} unique matches")

                    avg_confidence = total_confidence / len(all_matches) if all_matches else 0.0
                    result = {
                        "success": True,
                        "matches": merged_matches,
                        "confidence": avg_confidence,
                        "found": len(merged_matches) > 0,
                        "total_matches": len(merged_matches),
                        "search_text": secondary_text,
                        "adjusted_threshold": adjusted_threshold,
                        "processing_mode": "parallel_optimized"  # Indicate parallel processing was used
                    }
                    print(f"🔍 DEBUG: OPTIMIZED Final result: {result}")
                    return result

                except Exception as e:
                    print(f"❌ DEBUG: Parallel query failed: {e}")
                    print("🔄 DEBUG: Falling back to sequential processing")
                    # Fallback to original sequential method
                    return self.search_content_matches(secondary_transcription, threshold)
            else:
                print("❌ DEBUG: Index or embeddings not available for parallel query")
                return self.search_content_matches(secondary_transcription, threshold)
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Optimized content search failed: {str(e)}",
                "matches": [],
                "confidence": 0.0
            }
    
    def _search_single_chunk(self, chunk_text: str, adjusted_threshold: float) -> list:
        """
        Search a single secondary chunk embedding against Pinecone and return matches above threshold.
        Args:
            chunk_text: Text of the secondary chunk
            adjusted_threshold: Confidence threshold for matches
        Returns:
            List of Pinecone match objects above threshold
        """
        search_embedding = self.get_embedding(chunk_text)
        if not search_embedding:
            print("❌ DEBUG: Failed to generate embedding for chunk text")
            return []
        if self.index_name not in self.client.list_indexes().names():
            print(f"❌ DEBUG: Index '{self.index_name}' not found")
            return []
        self.index = self.client.Index(self.index_name)
        results = self.index.query(
            vector=search_embedding,
            top_k=10,
            include_metadata=True
        )
        query_matches = getattr(results, 'matches', [])
        filtered = [m for m in query_matches if getattr(m, 'score', 0.0) >= adjusted_threshold]
        print(f"🔍 DEBUG: _search_single_chunk found {len(filtered)} matches above threshold {adjusted_threshold}")
        return filtered
    
    def _search_with_embedding(self, embedding: List[float], adjusted_threshold: float) -> list:
        """
        Search using pre-generated embedding against Pinecone and return matches above threshold.
        Args:
            embedding: Pre-generated embedding vector
            adjusted_threshold: Confidence threshold for matches
        Returns:
            List of Pinecone match objects above threshold
        """
        if not embedding:
            print("❌ DEBUG: No embedding provided for search")
            return []
        if self.index_name not in self.client.list_indexes().names():
            print(f"❌ DEBUG: Index '{self.index_name}' not found")
            return []
        self.index = self.client.Index(self.index_name)
        results = self.index.query(
            vector=embedding,
            top_k=10,
            include_metadata=True
        )
        query_matches = getattr(results, 'matches', [])
        filtered = [m for m in query_matches if getattr(m, 'score', 0.0) >= adjusted_threshold]
        print(f"🔍 DEBUG: _search_with_embedding found {len(filtered)} matches above threshold {adjusted_threshold}")
        return filtered
    
    def _check_content_overlap(self, secondary_text: str, primary_text: str) -> bool:
        """
        Check if secondary text has actual content overlap with primary text
        
        Args:
            secondary_text: Text from secondary file
            primary_text: Text from primary file segment
            
        Returns:
            True if there's meaningful content overlap
        """
        # Normalize texts for comparison
        secondary_clean = secondary_text.lower().strip()
        primary_clean = primary_text.lower().strip()
        
        # Remove punctuation for better matching
        import re
        secondary_words = set(re.findall(r'\b\w+\b', secondary_clean))
        primary_words = set(re.findall(r'\b\w+\b', primary_clean))
        
        # Calculate word overlap
        if not secondary_words:
            return False
            
        overlap_words = secondary_words.intersection(primary_words)
        overlap_ratio = len(overlap_words) / len(secondary_words)
        
        # Dynamic overlap requirement based on content length
        secondary_length = len(secondary_text)
        if secondary_length < 100:  # Short content
            min_overlap_ratio = 0.7  # 70% for short content
        elif secondary_length > 500:  # Very long content
            min_overlap_ratio = 0.3  # 30% for very long content
        else:  # Medium content
            min_overlap_ratio = 0.5  # 50% for medium content
        
        print(f"🔍 DEBUG: Content overlap check - Secondary words: {len(secondary_words)}, Overlap: {len(overlap_words)}, Ratio: {overlap_ratio:.2f}, Required: {min_overlap_ratio:.2f}")
        
        return overlap_ratio >= min_overlap_ratio
    
    def _chunk_secondary_text(self, secondary_transcription: Dict[str, Any]) -> list:
        """
        Chunk the secondary transcription text using the same chunking logic as primary.
        Args:
            secondary_transcription: Transcription result from secondary file
        Returns:
            List of chunk dictionaries
        """
        from src.chunking_utils import ChunkingUtils
        import config
        return ChunkingUtils.chunk_transcription(secondary_transcription, config.CHUNKING_CONFIG)
    
    def _merge_overlapping_matches(self, matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Merge overlapping timestamp matches
        
        Args:
            matches: List of match dictionaries with timestamps
            
        Returns:
            List of merged matches
        """
        if not matches:
            return []
        
        # Sort matches by start time
        sorted_matches = sorted(matches, key=lambda x: x["start_time"])
        
        print(f"🔍 DEBUG: Merging {len(sorted_matches)} matches:")
        for i, match in enumerate(sorted_matches):
            print(f"  Match {i+1}: {match['start_time']:.2f}s - {match['end_time']:.2f}s (text: '{match['text'][:50]}...')")
        
        merged = []
        current_match = sorted_matches[0].copy()
        
        for match in sorted_matches[1:]:
            # Check if current match overlaps with the next one
            # Only merge if there's actual overlap (not just adjacent)
            # Use a very small tolerance for floating point precision
            overlap_tolerance = 0.01  # 10ms tolerance
            has_overlap = (match["start_time"] < (current_match["end_time"] + overlap_tolerance))
            
            print(f"🔍 DEBUG: Checking overlap: {current_match['start_time']:.2f}s-{current_match['end_time']:.2f}s vs {match['start_time']:.2f}s-{match['end_time']:.2f}s = {has_overlap}")
            
            if has_overlap:
                # Merge overlapping matches
                old_end = current_match["end_time"]
                current_match["end_time"] = max(current_match["end_time"], match["end_time"])
                current_match["confidence"] = max(current_match["confidence"], match["confidence"])
                print(f"🔍 DEBUG: Merged! New range: {current_match['start_time']:.2f}s - {current_match['end_time']:.2f}s (was {old_end:.2f}s)")
            else:
                # No overlap, add current match and start new one
                print(f"🔍 DEBUG: No overlap, adding current match: {current_match['start_time']:.2f}s - {current_match['end_time']:.2f}s")
                merged.append(current_match)
                current_match = match.copy()
        
        # Add the last match
        merged.append(current_match)
        print(f"🔍 DEBUG: Final merged matches: {len(merged)}")
        for i, match in enumerate(merged):
            print(f"  Final Match {i+1}: {match['start_time']:.2f}s - {match['end_time']:.2f}s")
        
        return merged
    
    def _wait_for_indexing(self, test_id: str, max_retries: int = 5, base_delay: float = 0.5) -> bool:
        """
        Wait for Pinecone to finish indexing upserted vectors.
        Args:
            test_id: A vector ID to test searchability (must be provided)
            max_retries: Maximum number of retries
            base_delay: Initial delay in seconds
        Returns:
            True if vectors are searchable, False otherwise
        """
        delay = base_delay
        for attempt in range(max_retries):
            try:
                if self.index is not None and test_id:
                    res = self.index.fetch(ids=[test_id])
                    if res and getattr(res, 'vectors', None):
                        if test_id in res.vectors:
                            return True
            except Exception:
                pass  # Ignore errors, just retry
            time.sleep(delay)
            delay *= 1.5  # Exponential backoff
        return False

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
            
            # Get all chunk texts for batch embedding
            chunk_texts = [chunk["text"] for chunk in chunks]
            
            # Generate embeddings in batch
            embeddings = self.get_embeddings_batch(chunk_texts)
            
            # Create vector records
            for chunk, embedding in zip(chunks, embeddings):
                if embedding:
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
                # Wait for indexing with longer timeout for better reliability
                first_id = vectors_to_upsert[0]["id"] if vectors_to_upsert else None
                if first_id:
                    print(f"⏳ DEBUG: Waiting for indexing to complete for {len(vectors_to_upsert)} vectors...")
                    if not self._wait_for_indexing(test_id=first_id, max_retries=10, base_delay=1.0):
                        print("⚠️ Pinecone indexing delay: vectors may not be immediately searchable (graceful degradation)")
                    else:
                        print("✅ DEBUG: Indexing completed successfully")
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
        
        print(f"🔍 DEBUG: Generating chunks from {len(segments)} Whisper segments:")
        for i, segment in enumerate(segments):
            start_time = segment.get("start", 0)
            end_time = segment.get("end", 0)
            text = segment.get("text", "").strip()
            print(f"  Segment {i+1}: {start_time:.2f}s - {end_time:.2f}s (text: '{text[:50]}...')")
        
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
                print(f"🔍 DEBUG: Segment {segment_index+1} is long ({len(text)} chars), splitting...")
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
        
        print(f"🔍 DEBUG: Generated {len(chunks)} total chunks")
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
            
            # Access matches from the query results
            return getattr(results, 'matches', [])
            
        except Exception as e:
            print(f"❌ Pinecone search failed: {e}")
            return [] 
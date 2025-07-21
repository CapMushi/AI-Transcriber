"""
Intelligent chunking utilities for transcription data
"""

import re
from typing import Dict, List, Any, Tuple
import config


class ChunkingUtils:
    """Utilities for intelligent chunking of transcription data"""
    
    @staticmethod
    def chunk_transcription(transcription_data: Dict[str, Any],
                           chunking_config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Chunk transcription data using intelligent strategies
        
        Args:
            transcription_data: Transcription result from Whisper
            chunking_config: Chunking configuration (optional)
            
        Returns:
            List of chunk dictionaries
        """
        if chunking_config is None:
            chunking_config = config.CHUNKING_CONFIG
        
        # Try segment-based chunking first
        if chunking_config.get("segment_based", True):
            chunks = ChunkingUtils._segment_based_chunking(
                transcription_data, chunking_config
            )
            if chunks:
                return chunks
        
        # Fallback to text-based chunking
        return ChunkingUtils._text_based_chunking(
            transcription_data, chunking_config
        )
    
    @staticmethod
    def _segment_based_chunking(transcription_data: Dict[str, Any],
                                chunking_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Chunk based on Whisper segments
        
        Args:
            transcription_data: Transcription result
            chunking_config: Chunking configuration
            
        Returns:
            List of chunk dictionaries
        """
        chunks = []
        segments = transcription_data.get("segments", [])
        
        if not segments:
            return []
        
        max_segment_length = chunking_config.get("max_segment_length", 500)
        
        for segment_index, segment in enumerate(segments):
            text = segment.get("text", "").strip()
            if not text:
                continue
            
            start_time = segment.get("start", 0)
            end_time = segment.get("end", 0)
            
            # Check if segment needs splitting
            if len(text) > max_segment_length:
                sub_chunks = ChunkingUtils._split_segment(
                    text, start_time, end_time, segment_index, chunking_config
                )
                chunks.extend(sub_chunks)
            else:
                # Use segment as-is
                chunk = ChunkingUtils._create_chunk_metadata(
                    text, start_time, end_time, segment_index,
                    "segment", transcription_data
                )
                chunks.append(chunk)
        
        return chunks
    
    @staticmethod
    def _split_segment(text: str,
                       start_time: float,
                       end_time: float,
                       segment_index: int,
                       chunking_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Split a long segment into smaller chunks
        
        Args:
            text: Segment text
            start_time: Start timestamp
            end_time: End timestamp
            segment_index: Original segment index
            chunking_config: Chunking configuration
            
        Returns:
            List of chunk dictionaries
        """
        chunks = []
        
        # Split by sentences first
        sentences = ChunkingUtils._split_into_sentences(text)
        
        current_time = start_time
        duration = end_time - start_time
        total_chars = len(text)
        
        if total_chars == 0:
            return []
        
        # Calculate time per character
        time_per_char = duration / total_chars if total_chars > 0 else 0
        
        for sentence_index, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Calculate sentence timing
            sentence_start = current_time
            sentence_chars = len(sentence)
            sentence_duration = sentence_chars * time_per_char
            sentence_end = sentence_start + sentence_duration
            
            # Create chunk for sentence
            chunk = ChunkingUtils._create_chunk_metadata(
                sentence, sentence_start, sentence_end, segment_index,
                "sentence", {}, chunk_index=sentence_index
            )
            chunks.append(chunk)
            
            # Update current time
            current_time = sentence_end
        
        return chunks
    
    @staticmethod
    def _split_into_sentences(text: str) -> List[str]:
        """
        Split text into sentences
        
        Args:
            text: Text to split
            
        Returns:
            List of sentences
        """
        # Simple sentence splitting - can be enhanced
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    @staticmethod
    def _text_based_chunking(transcription_data: Dict[str, Any],
                             chunking_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fallback text-based chunking
        
        Args:
            transcription_data: Transcription result
            chunking_config: Chunking configuration
            
        Returns:
            List of chunk dictionaries
        """
        text = transcription_data.get("text", "")
        if not text:
            return []
        
        chunk_size = chunking_config.get("max_chunk_size", 1000)
        overlap_size = chunking_config.get("overlap_size", 200)
        
        chunks = []
        words = text.split()
        total_words = len(words)
        
        if total_words == 0:
            return []
        
        current_pos = 0
        chunk_index = 0
        
        while current_pos < total_words:
            # Calculate chunk boundaries
            end_pos = min(current_pos + chunk_size, total_words)
            
            # Extract chunk text
            chunk_words = words[current_pos:end_pos]
            chunk_text = " ".join(chunk_words)
            
            # Create chunk
            chunk = ChunkingUtils._create_chunk_metadata(
                chunk_text, 0, 0, 0, "text_chunk", transcription_data,
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
    
    @staticmethod
    def _create_chunk_metadata(text: str,
                               start_time: float,
                               end_time: float,
                               segment_index: int,
                               chunk_type: str,
                               transcription_data: Dict[str, Any],
                               chunk_index: int = 0) -> Dict[str, Any]:
        """
        Create chunk metadata
        
        Args:
            text: Chunk text
            start_time: Start timestamp
            end_time: End timestamp
            segment_index: Original segment index
            chunk_type: Type of chunk
            transcription_data: Transcription result
            chunk_index: Chunk index within segment
            
        Returns:
            Chunk dictionary
        """
        return {
            "text": text,
            "start_time": start_time,
            "end_time": end_time,
            "segment_index": segment_index,
            "chunk_type": chunk_type,
            "chunk_index": chunk_index,
            "language": transcription_data.get("language", "unknown"),
            "model_used": transcription_data.get("model_used", "unknown"),
            "confidence": transcription_data.get("confidence", 0.0),
            "processing_time": transcription_data.get("processing_time", 0)
        }
    
    @staticmethod
    def validate_chunking_config(chunking_config: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate chunking configuration
        
        Args:
            chunking_config: Configuration to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        required_keys = [
            "segment_based", "max_segment_length", "min_chunk_size",
            "max_chunk_size", "overlap_size"
        ]
        
        for key in required_keys:
            if key not in chunking_config:
                return False, f"Missing required key: {key}"
        
        # Validate numeric values
        if chunking_config["max_chunk_size"] <= 0:
            return False, "max_chunk_size must be positive"
        
        if chunking_config["min_chunk_size"] <= 0:
            return False, "min_chunk_size must be positive"
        
        if chunking_config["overlap_size"] < 0:
            return False, "overlap_size must be non-negative"
        
        if chunking_config["max_segment_length"] <= 0:
            return False, "max_segment_length must be positive"
        
        return True, "Configuration is valid" 
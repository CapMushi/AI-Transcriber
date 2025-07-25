#!/usr/bin/env python3
"""
Test Sentence-Based Chunking Strategy
Compares current fixed-size chunking with sentence-based approach
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.transcriber import WhisperTranscriber
from src.audio_processor import AudioProcessor
from src.vector_store import PineconeVectorStore
from src.chunking_utils import ChunkingUtils
import config

class SentenceChunkingTester:
    """Test different chunking strategies"""
    
    def __init__(self):
        self.transcriber = WhisperTranscriber()
        self.audio_processor = AudioProcessor()
        self.vector_store = PineconeVectorStore()
    
    def create_sentence_chunking_config(self):
        """Create sentence-based chunking configuration"""
        return {
            "segment_based": True,
            "sentence_based": True,
            "max_sentences_per_chunk": 3,
            "min_chunk_size": 20,
            "max_chunk_size": 500,
            "overlap_size": 100,
            "preserve_timestamps": True,
            "preserve_context": True
        }
    
    def test_chunking_strategies(self, transcription_data: Dict[str, Any]):
        """Test different chunking strategies"""
        print(f"\n{'='*80}")
        print("CHUNKING STRATEGY COMPARISON")
        print(f"{'='*80}")
        
        # Current strategy
        print(f"\n1. CURRENT STRATEGY (Fixed-size chunks)")
        print(f"Config: {config.CHUNKING_CONFIG}")
        current_chunks = ChunkingUtils.chunk_transcription(transcription_data, config.CHUNKING_CONFIG)
        print(f"Generated {len(current_chunks)} chunks")
        
        # Analyze current chunks
        current_stats = self.analyze_chunks(current_chunks, "Current")
        
        # Sentence-based strategy
        print(f"\n2. SENTENCE-BASED STRATEGY")
        sentence_config = self.create_sentence_chunking_config()
        print(f"Config: {sentence_config}")
        
        # Note: This would require implementing sentence-based chunking in ChunkingUtils
        # For now, we'll simulate it
        sentence_chunks = self.simulate_sentence_chunking(transcription_data)
        print(f"Generated {len(sentence_chunks)} chunks")
        
        # Analyze sentence chunks
        sentence_stats = self.analyze_chunks(sentence_chunks, "Sentence")
        
        # Compare strategies
        self.compare_strategies(current_stats, sentence_stats)
        
        return current_chunks, sentence_chunks
    
    def simulate_sentence_chunking(self, transcription_data: Dict[str, Any]):
        """Simulate sentence-based chunking (placeholder for actual implementation)"""
        segments = transcription_data.get("segments", [])
        chunks = []
        
        current_chunk = {
            "text": "",
            "start_time": 0,
            "end_time": 0,
            "chunk_type": "sentence_based"
        }
        
        sentence_count = 0
        max_sentences = 3
        
        for segment in segments:
            text = segment.get("text", "").strip()
            start_time = segment.get("start", 0)
            end_time = segment.get("end", 0)
            
            # Simple sentence detection (ends with . ! ?)
            is_sentence_end = any(text.endswith(p) for p in ['.', '!', '?'])
            
            if current_chunk["text"]:
                current_chunk["text"] += " " + text
                current_chunk["end_time"] = end_time
            else:
                current_chunk["text"] = text
                current_chunk["start_time"] = start_time
                current_chunk["end_time"] = end_time
            
            sentence_count += 1
            
            # Create chunk if sentence ends or max sentences reached
            if is_sentence_end or sentence_count >= max_sentences:
                if current_chunk["text"]:
                    chunks.append(current_chunk.copy())
                    current_chunk = {
                        "text": "",
                        "start_time": 0,
                        "end_time": 0,
                        "chunk_type": "sentence_based"
                    }
                    sentence_count = 0
        
        # Add remaining chunk
        if current_chunk["text"]:
            chunks.append(current_chunk)
        
        return chunks
    
    def analyze_chunks(self, chunks: List[Dict], strategy_name: str):
        """Analyze chunk characteristics"""
        if not chunks:
            return {}
        
        chunk_lengths = [len(chunk.get("text", "")) for chunk in chunks]
        chunk_durations = [chunk.get("end_time", 0) - chunk.get("start_time", 0) for chunk in chunks]
        
        stats = {
            "strategy": strategy_name,
            "total_chunks": len(chunks),
            "avg_length": sum(chunk_lengths) / len(chunk_lengths),
            "min_length": min(chunk_lengths),
            "max_length": max(chunk_lengths),
            "avg_duration": sum(chunk_durations) / len(chunk_durations),
            "min_duration": min(chunk_durations),
            "max_duration": max(chunk_durations),
            "short_chunks": sum(1 for l in chunk_lengths if l < 50),
            "long_chunks": sum(1 for l in chunk_lengths if l > 200)
        }
        
        print(f"\n{strategy_name} Chunk Statistics:")
        print(f"  Total chunks: {stats['total_chunks']}")
        print(f"  Average length: {stats['avg_length']:.1f} chars")
        print(f"  Length range: {stats['min_length']} - {stats['max_length']} chars")
        print(f"  Average duration: {stats['avg_duration']:.2f}s")
        print(f"  Duration range: {stats['min_duration']:.2f}s - {stats['max_duration']:.2f}s")
        print(f"  Short chunks (<50 chars): {stats['short_chunks']}")
        print(f"  Long chunks (>200 chars): {stats['long_chunks']}")
        
        return stats
    
    def compare_strategies(self, current_stats: Dict, sentence_stats: Dict):
        """Compare the two chunking strategies"""
        print(f"\n{'='*80}")
        print("STRATEGY COMPARISON")
        print(f"{'='*80}")
        
        print(f"\nChunk Count:")
        print(f"  Current: {current_stats['total_chunks']}")
        print(f"  Sentence: {sentence_stats['total_chunks']}")
        
        print(f"\nAverage Chunk Length:")
        print(f"  Current: {current_stats['avg_length']:.1f} chars")
        print(f"  Sentence: {sentence_stats['avg_length']:.1f} chars")
        
        print(f"\nShort Chunks (<50 chars):")
        print(f"  Current: {current_stats['short_chunks']}")
        print(f"  Sentence: {sentence_stats['short_chunks']}")
        
        print(f"\nLong Chunks (>200 chars):")
        print(f"  Current: {current_stats['long_chunks']}")
        print(f"  Sentence: {sentence_stats['long_chunks']}")
        
        # Predict potential improvements
        improvement = sentence_stats['short_chunks'] - current_stats['short_chunks']
        if improvement < 0:
            print(f"\n✅ Sentence-based chunking reduces short chunks by {abs(improvement)}")
        else:
            print(f"\n⚠️ Sentence-based chunking increases short chunks by {improvement}")
    
    def test_multi_threshold_search(self, primary_file: str, secondary_file: str):
        """Test multi-threshold search strategy"""
        print(f"\n{'='*80}")
        print("MULTI-THRESHOLD SEARCH TEST")
        print(f"{'='*80}")
        
        # Process files
        primary_audio = self.audio_processor.prepare_audio_for_whisper_fast(primary_file)[1]
        primary_transcription = self.transcriber.transcribe_audio(audio_path=primary_audio)
        
        secondary_audio = self.audio_processor.prepare_audio_for_whisper_fast(secondary_file)[1]
        secondary_transcription = self.transcriber.transcribe_audio(audio_path=secondary_audio)
        
        # Store primary content
        self.vector_store.clear_existing_embeddings()
        file_metadata = {
            "filename": Path(primary_file).name,
            "file_path": primary_file,
            "file_type": "primary",
            "debug_session": True
        }
        
        store_success = self.vector_store.store_transcription_chunks(
            file_id=f"multi_threshold_test_{int(time.time())}",
            transcription_data=primary_transcription,
            file_metadata=file_metadata
        )
        
        if not store_success:
            print("Failed to store primary content")
            return
        
        # Test different thresholds
        thresholds = [0.9, 0.8, 0.7, 0.6, 0.5, 0.4]
        
        print(f"\nTesting thresholds: {thresholds}")
        
        for threshold in thresholds:
            print(f"\nThreshold: {threshold}")
            search_result = self.vector_store.search_content_matches_optimized(
                secondary_transcription=secondary_transcription,
                threshold=threshold
            )
            
            if search_result.get("success", False):
                matches = search_result.get("matches", [])
                print(f"  Found {len(matches)} matches")
                
                # Show match details
                for i, match in enumerate(matches[:3]):
                    print(f"    Match {i+1}: {match['start_time']:.2f}s - {match['end_time']:.2f}s")
                    print(f"      Confidence: {match.get('confidence', 0):.3f}")
                    print(f"      Text: '{match.get('text', '')[:50]}...'")
            else:
                print(f"  Search failed: {search_result.get('error')}")
    
    def run_complete_test(self, primary_file: str, secondary_file: str):
        """Run complete testing of different strategies"""
        print(f"COMPLETE CHUNKING STRATEGY TEST")
        print(f"{'='*80}")
        print(f"Primary file: {primary_file}")
        print(f"Secondary file: {secondary_file}")
        
        # Process primary file
        print(f"\nProcessing primary file...")
        primary_audio = self.audio_processor.prepare_audio_for_whisper_fast(primary_file)[1]
        primary_transcription = self.transcriber.transcribe_audio(audio_path=primary_audio)
        
        if not primary_transcription.get("success", False):
            print(f"Primary transcription failed: {primary_transcription.get('error')}")
            return
        
        # Test chunking strategies
        current_chunks, sentence_chunks = self.test_chunking_strategies(primary_transcription)
        
        # Test multi-threshold search
        self.test_multi_threshold_search(primary_file, secondary_file)
        
        print(f"\n{'='*80}")
        print("TESTING COMPLETE")
        print(f"{'='*80}")

def main():
    """Main function"""
    if len(sys.argv) != 3:
        print("Usage: python test_sentence_chunking.py <primary_file> <secondary_file>")
        print("Example: python test_sentence_chunking.py primary.mp4 secondary.mp4")
        sys.exit(1)
    
    primary_file = sys.argv[1]
    secondary_file = sys.argv[2]
    
    # Validate files exist
    if not os.path.exists(primary_file):
        print(f"Error: Primary file not found: {primary_file}")
        sys.exit(1)
    
    if not os.path.exists(secondary_file):
        print(f"Error: Secondary file not found: {secondary_file}")
        sys.exit(1)
    
    # Run test
    tester = SentenceChunkingTester()
    tester.run_complete_test(primary_file, secondary_file)

if __name__ == "__main__":
    main() 
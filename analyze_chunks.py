#!/usr/bin/env python3
"""
Advanced Chunk Analysis Script
Provides detailed analysis of chunking and matching processes
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.transcriber import WhisperTranscriber
from src.audio_processor import AudioProcessor
from src.vector_store import PineconeVectorStore
from src.chunking_utils import ChunkingUtils
import config

class ChunkAnalyzer:
    """Advanced analyzer for chunking and matching issues"""
    
    def __init__(self):
        self.transcriber = WhisperTranscriber()
        self.audio_processor = AudioProcessor()
        self.vector_store = PineconeVectorStore()
    
    def analyze_chunking_process(self, transcription_data: Dict[str, Any], file_type: str):
        """Analyze the chunking process in detail"""
        print(f"\n{'='*60}")
        print(f"CHUNKING ANALYSIS: {file_type.upper()}")
        print(f"{'='*60}")
        
        segments = transcription_data.get("segments", [])
        print(f"Total segments: {len(segments)}")
        
        # Analyze segment distribution
        segment_lengths = []
        segment_durations = []
        
        for i, segment in enumerate(segments):
            text = segment.get("text", "").strip()
            start_time = segment.get("start", 0)
            end_time = segment.get("end", 0)
            duration = end_time - start_time
            
            segment_lengths.append(len(text))
            segment_durations.append(duration)
            
            if i < 10:  # Show first 10 segments
                print(f"Segment {i+1}: {start_time:.2f}s - {end_time:.2f}s ({duration:.2f}s)")
                print(f"  Text: '{text}'")
                print(f"  Length: {len(text)} chars")
        
        # Statistics
        if segment_lengths:
            avg_length = sum(segment_lengths) / len(segment_lengths)
            max_length = max(segment_lengths)
            min_length = min(segment_lengths)
            print(f"\nText length statistics:")
            print(f"  Average: {avg_length:.1f} chars")
            print(f"  Min: {min_length} chars")
            print(f"  Max: {max_length} chars")
        
        if segment_durations:
            avg_duration = sum(segment_durations) / len(segment_durations)
            max_duration = max(segment_durations)
            min_duration = min(segment_durations)
            print(f"\nDuration statistics:")
            print(f"  Average: {avg_duration:.2f}s")
            print(f"  Min: {min_duration:.2f}s")
            print(f"  Max: {max_duration:.2f}s")
        
        # Chunk the transcription
        print(f"\nChunking with config: {config.CHUNKING_CONFIG}")
        chunks = ChunkingUtils.chunk_transcription(transcription_data, config.CHUNKING_CONFIG)
        print(f"Generated {len(chunks)} chunks")
        
        # Analyze chunks
        chunk_lengths = []
        chunk_durations = []
        
        for i, chunk in enumerate(chunks):
            text = chunk.get("text", "").strip()
            start_time = chunk.get("start_time", 0)
            end_time = chunk.get("end_time", 0)
            duration = end_time - start_time
            
            chunk_lengths.append(len(text))
            chunk_durations.append(duration)
            
            if i < 10:  # Show first 10 chunks
                print(f"Chunk {i+1}: {start_time:.2f}s - {end_time:.2f}s ({duration:.2f}s)")
                print(f"  Text: '{text}'")
                print(f"  Length: {len(text)} chars")
                print(f"  Type: {chunk.get('chunk_type', 'unknown')}")
        
        # Chunk statistics
        if chunk_lengths:
            avg_chunk_length = sum(chunk_lengths) / len(chunk_lengths)
            max_chunk_length = max(chunk_lengths)
            min_chunk_length = min(chunk_lengths)
            print(f"\nChunk length statistics:")
            print(f"  Average: {avg_chunk_length:.1f} chars")
            print(f"  Min: {min_chunk_length} chars")
            print(f"  Max: {max_chunk_length} chars")
        
        if chunk_durations:
            avg_chunk_duration = sum(chunk_durations) / len(chunk_durations)
            max_chunk_duration = max(chunk_durations)
            min_chunk_duration = min(chunk_durations)
            print(f"\nChunk duration statistics:")
            print(f"  Average: {avg_chunk_duration:.2f}s")
            print(f"  Min: {min_chunk_duration:.2f}s")
            print(f"  Max: {max_chunk_duration:.2f}s")
        
        return chunks
    
    def analyze_embedding_similarity(self, primary_chunks: List[Dict], secondary_chunks: List[Dict]):
        """Analyze embedding similarity between primary and secondary chunks"""
        print(f"\n{'='*60}")
        print("EMBEDDING SIMILARITY ANALYSIS")
        print(f"{'='*60}")
        
        if not primary_chunks or not secondary_chunks:
            print("No chunks to analyze")
            return
        
        print(f"Primary chunks: {len(primary_chunks)}")
        print(f"Secondary chunks: {len(secondary_chunks)}")
        
        # Generate embeddings for secondary chunks
        secondary_texts = [chunk.get("text", "").strip() for chunk in secondary_chunks]
        secondary_embeddings = self.vector_store.get_embeddings_batch(secondary_texts)
        
        if not secondary_embeddings or all(emb is None for emb in secondary_embeddings):
            print("Failed to generate secondary embeddings")
            return
        
        # Test similarity with different thresholds
        thresholds = [0.5, 0.6, 0.7, 0.8, 0.9, 0.95]
        
        for threshold in thresholds:
            print(f"\nTesting threshold: {threshold}")
            matches_found = 0
            
            for i, (chunk_text, embedding) in enumerate(zip(secondary_texts, secondary_embeddings)):
                if not embedding:
                    continue
                
                # Search with this embedding
                search_results = self.vector_store._search_with_embedding_optimized(
                    embedding, chunk_text, threshold
                )
                
                if search_results:
                    matches_found += len(search_results)
                    print(f"  Chunk {i+1}: {len(search_results)} matches")
                    for match in search_results[:3]:  # Show first 3 matches
                        confidence = getattr(match, 'score', 0.0)
                        metadata = getattr(match, 'metadata', {})
                        print(f"    Match: {confidence:.3f} confidence")
                        print(f"      Time: {metadata.get('start_time', 0):.2f}s - {metadata.get('end_time', 0):.2f}s")
                        print(f"      Text: '{metadata.get('text', '')[:50]}...'")
                else:
                    print(f"  Chunk {i+1}: No matches")
            
            print(f"  Total matches at threshold {threshold}: {matches_found}")
    
    def analyze_missing_content(self, primary_segments: List[Dict], found_matches: List[Dict]):
        """Analyze what content is missing from the matches"""
        print(f"\n{'='*60}")
        print("MISSING CONTENT ANALYSIS")
        print(f"{'='*60}")
        
        if not found_matches:
            print("No matches found - all content is missing")
            return
        
        # Sort matches by start time
        sorted_matches = sorted(found_matches, key=lambda x: x["start_time"])
        
        # Find all gaps
        gaps = []
        current_end = 0.0
        
        for match in sorted_matches:
            match_start = match["start_time"]
            match_end = match["end_time"]
            
            # Check for gap before this match
            if match_start > current_end:
                gap = {
                    "start_time": current_end,
                    "end_time": match_start,
                    "duration": match_start - current_end
                }
                gaps.append(gap)
            
            current_end = max(current_end, match_end)
        
        # Check for gap after last match
        if primary_segments:
            last_segment = max(primary_segments, key=lambda x: x["end"])
            primary_end = last_segment["end"]
            
            if current_end < primary_end:
                gap = {
                    "start_time": current_end,
                    "end_time": primary_end,
                    "duration": primary_end - current_end
                }
                gaps.append(gap)
        
        print(f"Found {len(gaps)} gaps in matches")
        
        # Analyze each gap
        for i, gap in enumerate(gaps):
            print(f"\nGap {i+1}: {gap['start_time']:.2f}s - {gap['end_time']:.2f}s (duration: {gap['duration']:.2f}s)")
            
            # Find segments in this gap
            gap_segments = []
            gap_text = ""
            
            for segment in primary_segments:
                segment_start = segment.get("start", 0)
                segment_end = segment.get("end", 0)
                
                # Check if segment overlaps with gap
                if (segment_start < gap["end_time"] and segment_end > gap["start_time"]):
                    overlap_start = max(segment_start, gap["start_time"])
                    overlap_end = min(segment_end, gap["end_time"])
                    segment_text = segment.get("text", "")
                    
                    gap_segments.append({
                        "segment": segment,
                        "overlap_start": overlap_start,
                        "overlap_end": overlap_end,
                        "text": segment_text
                    })
                    
                    gap_text += segment_text + " "
            
            print(f"  Segments in gap: {len(gap_segments)}")
            print(f"  Total text in gap: {len(gap_text.strip())} characters")
            print(f"  Gap text: '{gap_text.strip()}'")
            
            # Analyze why this gap might be missing
            if gap_segments:
                avg_segment_length = sum(len(seg["text"]) for seg in gap_segments) / len(gap_segments)
                print(f"  Average segment length: {avg_segment_length:.1f} characters")
                
                # Check if segments are very short
                short_segments = [seg for seg in gap_segments if len(seg["text"]) < 50]
                if short_segments:
                    print(f"  Short segments (<50 chars): {len(short_segments)}")
                    for seg in short_segments[:3]:
                        print(f"    '{seg['text']}'")
                
                # Check if segments have low confidence
                low_confidence_segments = []
                for seg in gap_segments:
                    segment_data = seg["segment"]
                    avg_logprob = segment_data.get("avg_logprob", -1.0)
                    confidence = max(0, min(100, (avg_logprob + 1) * 100))
                    if confidence < 50:
                        low_confidence_segments.append((confidence, seg["text"]))
                
                if low_confidence_segments:
                    print(f"  Low confidence segments (<50%): {len(low_confidence_segments)}")
                    for confidence, text in low_confidence_segments[:3]:
                        print(f"    {confidence:.1f}%: '{text}'")
    
    def run_complete_analysis(self, primary_file: str, secondary_file: str):
        """Run complete analysis of both files"""
        # Create output file for results
        timestamp = int(time.time())
        output_file = f"chunk_analysis_{timestamp}.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"COMPLETE CHUNK ANALYSIS\n")
            f.write(f"{'='*80}\n")
            f.write(f"Primary file: {primary_file}\n")
            f.write(f"Secondary file: {secondary_file}\n")
            f.write(f"Analysis timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            print(f"COMPLETE CHUNK ANALYSIS")
            print(f"{'='*80}")
            print(f"Primary file: {primary_file}")
            print(f"Secondary file: {secondary_file}")
            print(f"Results will be saved to: {output_file}")
            
            # Process primary file
            print(f"\nProcessing primary file...")
            f.write(f"\nProcessing primary file...\n")
            primary_audio = self.audio_processor.prepare_audio_for_whisper_fast(primary_file)[1]
            primary_transcription = self.transcriber.transcribe_audio(audio_path=primary_audio)
            
            if not primary_transcription.get("success", False):
                error_msg = f"Primary transcription failed: {primary_transcription.get('error')}"
                print(error_msg)
                f.write(f"{error_msg}\n")
                return
            
            # Analyze primary chunking
            primary_chunks = self.analyze_chunking_process(primary_transcription, "PRIMARY")
            
            # Store primary content
            print(f"\nStoring primary content...")
            f.write(f"\nStoring primary content...\n")
            file_metadata = {
                "filename": Path(primary_file).name,
                "file_path": primary_file,
                "file_type": "primary",
                "debug_session": True
            }
            
            self.vector_store.clear_existing_embeddings()
            store_success = self.vector_store.store_transcription_chunks(
                file_id=f"analysis_{timestamp}",
                transcription_data=primary_transcription,
                file_metadata=file_metadata
            )
            
            if not store_success:
                error_msg = "Failed to store primary content"
                print(error_msg)
                f.write(f"{error_msg}\n")
                return
            
            # Process secondary file
            print(f"\nProcessing secondary file...")
            f.write(f"\nProcessing secondary file...\n")
            secondary_audio = self.audio_processor.prepare_audio_for_whisper_fast(secondary_file)[1]
            secondary_transcription = self.transcriber.transcribe_audio(audio_path=secondary_audio)
            
            if not secondary_transcription.get("success", False):
                error_msg = f"Secondary transcription failed: {secondary_transcription.get('error')}"
                print(error_msg)
                f.write(f"{error_msg}\n")
                return
            
            # Analyze secondary chunking
            secondary_chunks = self.analyze_chunking_process(secondary_transcription, "SECONDARY")
            
            # Analyze embedding similarity
            self.analyze_embedding_similarity(primary_chunks, secondary_chunks)
            
            # Search for matches
            print(f"\nSearching for matches...")
            f.write(f"\nSearching for matches...\n")
            search_result = self.vector_store.search_content_matches_optimized(
                secondary_transcription=secondary_transcription,
                threshold=0.7
            )
            
            if search_result.get("success", False):
                matches = search_result.get("matches", [])
                match_msg = f"Found {len(matches)} matches"
                print(match_msg)
                f.write(f"{match_msg}\n")
                
                # Analyze missing content
                self.analyze_missing_content(
                    primary_transcription.get("segments", []),
                    matches
                )
            else:
                error_msg = f"Search failed: {search_result.get('error')}"
                print(error_msg)
                f.write(f"{error_msg}\n")
            
            # Write summary to file
            f.write(f"\n{'='*80}\n")
            f.write(f"ANALYSIS COMPLETE\n")
            f.write(f"Output file: {output_file}\n")
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            print(f"\nAnalysis complete! Results saved to: {output_file}")

def main():
    """Main function"""
    if len(sys.argv) != 3:
        print("Usage: python analyze_chunks.py <primary_file> <secondary_file>")
        print("Example: python analyze_chunks.py primary.mp4 secondary.mp4")
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
    
    # Run analysis
    analyzer = ChunkAnalyzer()
    analyzer.run_complete_analysis(primary_file, secondary_file)

if __name__ == "__main__":
    main() 
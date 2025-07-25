#!/usr/bin/env python3
"""
Debug Script for Content Comparison
Replicates the original workflow and logs comprehensive information to identify missed chunks
"""

import os
import sys
import time
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.transcriber import WhisperTranscriber
from src.audio_processor import AudioProcessor
from src.output_formatter import OutputFormatter
from src.vector_store import PineconeVectorStore
from src.chunking_utils import ChunkingUtils
import config

# Configure comprehensive logging
def setup_logging(log_file: str):
    """Setup comprehensive logging to file"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, mode='w'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

class ComparisonDebugger:
    """Debug class to replicate the original workflow with detailed logging"""
    
    def __init__(self, log_file: str = "comparison_debug.log"):
        self.logger = setup_logging(log_file)
        self.transcriber = WhisperTranscriber()
        self.audio_processor = AudioProcessor()
        self.output_formatter = OutputFormatter()
        self.vector_store = PineconeVectorStore()
        
        self.logger.info("=" * 80)
        self.logger.info("COMPARISON DEBUG SESSION STARTED")
        self.logger.info("=" * 80)
        self.logger.info(f"Timestamp: {datetime.now()}")
        self.logger.info(f"Config: {config.CHUNKING_CONFIG}")
        self.logger.info("=" * 80)
    
    def log_file_info(self, file_path: str, file_type: str):
        """Log detailed file information"""
        self.logger.info(f"\n{'='*50}")
        self.logger.info(f"FILE INFO: {file_type.upper()}")
        self.logger.info(f"{'='*50}")
        
        file_path_obj = Path(file_path)
        self.logger.info(f"File path: {file_path}")
        self.logger.info(f"File exists: {file_path_obj.exists()}")
        if file_path_obj.exists():
            self.logger.info(f"File size: {file_path_obj.stat().st_size} bytes")
            self.logger.info(f"File extension: {file_path_obj.suffix}")
        
        # Validate file
        is_valid, error_msg = self.audio_processor.validate_file(file_path)
        self.logger.info(f"File validation: {'PASS' if is_valid else 'FAIL'}")
        if not is_valid:
            self.logger.error(f"Validation error: {error_msg}")
            return False
        
        # Get file info
        file_info = self.audio_processor.get_file_info(file_path)
        self.logger.info(f"File info: {json.dumps(file_info, indent=2)}")
        return True
    
    def prepare_audio(self, file_path: str, file_type: str):
        """Prepare audio for transcription with detailed logging"""
        self.logger.info(f"\n{'='*50}")
        self.logger.info(f"AUDIO PREPARATION: {file_type.upper()}")
        self.logger.info(f"{'='*50}")
        
        self.logger.info(f"Preparing audio for: {file_path}")
        success, audio_path = self.audio_processor.prepare_audio_for_whisper_fast(file_path)
        
        if not success:
            self.logger.error(f"Audio preparation failed: {audio_path}")
            return None
        
        self.logger.info(f"Audio prepared successfully: {audio_path}")
        
        # Log audio file details
        audio_path_obj = Path(audio_path)
        if audio_path_obj.exists():
            self.logger.info(f"Prepared audio size: {audio_path_obj.stat().st_size} bytes")
        
        return audio_path
    
    def transcribe_file(self, audio_path: str, file_type: str, model: str = "base", language: str = "auto"):
        """Transcribe file with detailed logging"""
        self.logger.info(f"\n{'='*50}")
        self.logger.info(f"TRANSCRIPTION: {file_type.upper()}")
        self.logger.info(f"{'='*50}")
        
        self.logger.info(f"Model: {model}")
        self.logger.info(f"Language: {language}")
        self.logger.info(f"Audio path: {audio_path}")
        
        start_time = time.time()
        result = self.transcriber.transcribe_audio(
            audio_path=audio_path,
            language=language if language != "auto" else None,
            task="transcribe",
            model=model
        )
        processing_time = time.time() - start_time
        
        self.logger.info(f"Transcription completed in {processing_time:.2f} seconds")
        
        if not result.get("success", False):
            self.logger.error(f"Transcription failed: {result.get('error', 'Unknown error')}")
            return None
        
        # Log transcription details
        self.logger.info(f"Success: {result.get('success')}")
        self.logger.info(f"Language detected: {result.get('language', 'unknown')}")
        self.logger.info(f"Confidence: {result.get('confidence', 0.0):.3f}")
        self.logger.info(f"Text length: {len(result.get('text', ''))} characters")
        self.logger.info(f"Number of segments: {len(result.get('segments', []))}")
        
        # Log first few segments
        segments = result.get('segments', [])
        self.logger.info(f"\nFirst 5 segments:")
        for i, segment in enumerate(segments[:5]):
            self.logger.info(f"  Segment {i+1}: {segment.get('start', 0):.2f}s - {segment.get('end', 0):.2f}s")
            self.logger.info(f"    Text: '{segment.get('text', '')}'")
        
        if len(segments) > 5:
            self.logger.info(f"  ... and {len(segments) - 5} more segments")
        
        return result
    
    def store_primary_content(self, transcription_data: Dict[str, Any], file_metadata: Dict[str, Any]):
        """Store primary content with detailed logging"""
        self.logger.info(f"\n{'='*50}")
        self.logger.info("STORING PRIMARY CONTENT")
        self.logger.info(f"{'='*50}")
        
        # Clear existing embeddings first
        self.logger.info("Clearing existing embeddings...")
        clear_success = self.vector_store.clear_existing_embeddings()
        self.logger.info(f"Clear embeddings result: {clear_success}")
        
        # Generate file ID
        file_id = f"debug_{int(time.time())}"
        self.logger.info(f"Generated file ID: {file_id}")
        
        # Store chunks
        self.logger.info("Storing transcription chunks...")
        store_success = self.vector_store.store_transcription_chunks(
            file_id=file_id,
            transcription_data=transcription_data,
            file_metadata=file_metadata
        )
        
        self.logger.info(f"Store chunks result: {store_success}")
        
        # Check if chunks were stored
        if store_success:
            existing_chunks = self.vector_store.check_existing_chunks(file_metadata)
            self.logger.info(f"Chunks exist in database: {existing_chunks}")
        
        return store_success
    
    def chunk_secondary_text(self, secondary_transcription: Dict[str, Any]):
        """Chunk secondary text with detailed logging"""
        self.logger.info(f"\n{'='*50}")
        self.logger.info("CHUNKING SECONDARY TEXT")
        self.logger.info(f"{'='*50}")
        
        self.logger.info(f"Chunking config: {json.dumps(config.CHUNKING_CONFIG, indent=2)}")
        
        # Use the same chunking logic as the original
        chunks = ChunkingUtils.chunk_transcription(secondary_transcription, config.CHUNKING_CONFIG)
        
        self.logger.info(f"Generated {len(chunks)} chunks")
        
        # Log each chunk in detail
        for i, chunk in enumerate(chunks):
            self.logger.info(f"\nChunk {i+1}:")
            self.logger.info(f"  Text: '{chunk.get('text', '')}'")
            self.logger.info(f"  Start time: {chunk.get('start_time', 0):.2f}s")
            self.logger.info(f"  End time: {chunk.get('end_time', 0):.2f}s")
            self.logger.info(f"  Segment index: {chunk.get('segment_index', 0)}")
            self.logger.info(f"  Chunk type: {chunk.get('chunk_type', 'unknown')}")
            self.logger.info(f"  Text length: {len(chunk.get('text', ''))} characters")
        
        return chunks
    
    def search_content_matches(self, secondary_transcription: Dict[str, Any], threshold: float = 0.7):
        """Search for content matches with detailed logging"""
        self.logger.info(f"\n{'='*50}")
        self.logger.info("SEARCHING FOR CONTENT MATCHES")
        self.logger.info(f"{'='*50}")
        
        self.logger.info(f"Threshold: {threshold}")
        self.logger.info(f"Secondary text: '{secondary_transcription.get('text', '')}'")
        
        # Use the optimized search method
        search_result = self.vector_store.search_content_matches_optimized(
            secondary_transcription=secondary_transcription,
            threshold=threshold
        )
        
        self.logger.info(f"Search result: {json.dumps(search_result, indent=2)}")
        
        return search_result
    
    def analyze_missing_regions(self, primary_segments: List[Dict], found_matches: List[Dict]):
        """Analyze regions that might be missing from matches"""
        self.logger.info(f"\n{'='*50}")
        self.logger.info("ANALYZING MISSING REGIONS")
        self.logger.info(f"{'='*50}")
        
        if not found_matches:
            self.logger.info("No matches found - all regions are missing")
            return
        
        # Sort matches by start time
        sorted_matches = sorted(found_matches, key=lambda x: x["start_time"])
        
        # Find gaps between matches
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
                self.logger.info(f"Gap found: {gap['start_time']:.2f}s - {gap['end_time']:.2f}s (duration: {gap['duration']:.2f}s)")
            
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
                self.logger.info(f"Final gap found: {gap['start_time']:.2f}s - {gap['end_time']:.2f}s (duration: {gap['duration']:.2f}s)")
        
        # Analyze what content is in the gaps
        self.logger.info(f"\nAnalyzing content in gaps:")
        for i, gap in enumerate(gaps):
            self.logger.info(f"\nGap {i+1}: {gap['start_time']:.2f}s - {gap['end_time']:.2f}s")
            
            # Find segments that fall within this gap
            gap_segments = []
            for segment in primary_segments:
                segment_start = segment.get("start", 0)
                segment_end = segment.get("end", 0)
                
                # Check if segment overlaps with gap
                if (segment_start < gap["end_time"] and segment_end > gap["start_time"]):
                    overlap_start = max(segment_start, gap["start_time"])
                    overlap_end = min(segment_end, gap["end_time"])
                    gap_segments.append({
                        "segment": segment,
                        "overlap_start": overlap_start,
                        "overlap_end": overlap_end,
                        "text": segment.get("text", "")
                    })
            
            self.logger.info(f"  Segments in gap: {len(gap_segments)}")
            for seg in gap_segments:
                self.logger.info(f"    {seg['overlap_start']:.2f}s - {seg['overlap_end']:.2f}s: '{seg['text']}'")
        
        return gaps
    
    def run_comparison_debug(self, primary_file: str, secondary_file: str, threshold: float = 0.7):
        """Run the complete comparison debug workflow"""
        self.logger.info(f"\n{'='*80}")
        self.logger.info("STARTING COMPARISON DEBUG WORKFLOW")
        self.logger.info(f"{'='*80}")
        self.logger.info(f"Primary file: {primary_file}")
        self.logger.info(f"Secondary file: {secondary_file}")
        self.logger.info(f"Threshold: {threshold}")
        
        # Step 1: Process Primary File
        self.logger.info(f"\n{'='*50}")
        self.logger.info("STEP 1: PROCESSING PRIMARY FILE")
        self.logger.info(f"{'='*50}")
        
        if not self.log_file_info(primary_file, "PRIMARY"):
            return False
        
        primary_audio = self.prepare_audio(primary_file, "PRIMARY")
        if not primary_audio:
            return False
        
        primary_transcription = self.transcribe_file(primary_audio, "PRIMARY")
        if not primary_transcription:
            return False
        
        # Step 2: Store Primary Content
        self.logger.info(f"\n{'='*50}")
        self.logger.info("STEP 2: STORING PRIMARY CONTENT")
        self.logger.info(f"{'='*50}")
        
        file_metadata = {
            "filename": Path(primary_file).name,
            "file_path": primary_file,
            "file_type": "primary",
            "debug_session": True
        }
        
        store_success = self.store_primary_content(primary_transcription, file_metadata)
        if not store_success:
            self.logger.error("Failed to store primary content")
            return False
        
        # Step 3: Process Secondary File
        self.logger.info(f"\n{'='*50}")
        self.logger.info("STEP 3: PROCESSING SECONDARY FILE")
        self.logger.info(f"{'='*50}")
        
        if not self.log_file_info(secondary_file, "SECONDARY"):
            return False
        
        secondary_audio = self.prepare_audio(secondary_file, "SECONDARY")
        if not secondary_audio:
            return False
        
        secondary_transcription = self.transcribe_file(secondary_audio, "SECONDARY")
        if not secondary_transcription:
            return False
        
        # Step 4: Chunk Secondary Text
        secondary_chunks = self.chunk_secondary_text(secondary_transcription)
        
        # Step 5: Search for Matches
        search_result = self.search_content_matches(secondary_transcription, threshold)
        
        # Step 6: Analyze Results
        self.logger.info(f"\n{'='*50}")
        self.logger.info("STEP 6: ANALYZING RESULTS")
        self.logger.info(f"{'='*50}")
        
        if search_result.get("success", False):
            matches = search_result.get("matches", [])
            self.logger.info(f"Found {len(matches)} matches")
            
            # Analyze missing regions
            self.analyze_missing_regions(
                primary_transcription.get("segments", []),
                matches
            )
            
            # Log detailed match information
            self.logger.info(f"\nDetailed match information:")
            for i, match in enumerate(matches):
                self.logger.info(f"\nMatch {i+1}:")
                self.logger.info(f"  Start time: {match.get('start_time', 0):.2f}s")
                self.logger.info(f"  End time: {match.get('end_time', 0):.2f}s")
                self.logger.info(f"  Duration: {match.get('end_time', 0) - match.get('start_time', 0):.2f}s")
                self.logger.info(f"  Confidence: {match.get('confidence', 0):.3f}")
                self.logger.info(f"  Text: '{match.get('text', '')}'")
        else:
            self.logger.error(f"Search failed: {search_result.get('error', 'Unknown error')}")
        
        # Step 7: Summary
        self.logger.info(f"\n{'='*80}")
        self.logger.info("DEBUG SESSION SUMMARY")
        self.logger.info(f"{'='*80}")
        self.logger.info(f"Primary file processed: {primary_file}")
        self.logger.info(f"Secondary file processed: {secondary_file}")
        self.logger.info(f"Primary text length: {len(primary_transcription.get('text', ''))} characters")
        self.logger.info(f"Secondary text length: {len(secondary_transcription.get('text', ''))} characters")
        self.logger.info(f"Primary segments: {len(primary_transcription.get('segments', []))}")
        self.logger.info(f"Secondary chunks: {len(secondary_chunks)}")
        self.logger.info(f"Search threshold: {threshold}")
        self.logger.info(f"Matches found: {len(search_result.get('matches', []))}")
        self.logger.info(f"Search success: {search_result.get('success', False)}")
        
        return True

def main():
    """Main function to run the debug script"""
    if len(sys.argv) != 3:
        print("Usage: python debug_comparison.py <primary_file> <secondary_file>")
        print("Example: python debug_comparison.py primary.mp4 secondary.mp4")
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
    
    # Create debugger and run
    debugger = ComparisonDebugger()
    success = debugger.run_comparison_debug(primary_file, secondary_file)
    
    if success:
        print("\n✅ Debug session completed successfully!")
        print("Check 'comparison_debug.log' for detailed information.")
    else:
        print("\n❌ Debug session failed!")
        print("Check 'comparison_debug.log' for error details.")
        sys.exit(1)

if __name__ == "__main__":
    main() 
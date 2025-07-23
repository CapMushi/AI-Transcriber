#!/usr/bin/env python3
"""
Comprehensive timing analysis for the complete comparison workflow
Measures every step: primary storage + secondary comparison
"""

import time
import sys
import os
import asyncio
import concurrent.futures
from typing import Dict, Any, List, Tuple
import json

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.audio_processor import AudioProcessor
from src.transcriber import WhisperTranscriber
from src.vector_store import PineconeVectorStore
from src.chunking_utils import ChunkingUtils
from api.utils.vector_handler import VectorHandler
import config


class ComprehensiveComparisonTimingAnalyzer:
    """Analyzes timing for the complete comparison workflow"""
    
    def __init__(self):
        """Initialize components"""
        self.audio_processor = AudioProcessor()
        self.transcriber = WhisperTranscriber()
        self.vector_store = PineconeVectorStore()
        self.vector_handler = VectorHandler()
        self.chunking_utils = ChunkingUtils()
        
    def measure_file_validation(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """Measure file validation timing"""
        print(f"🔍 Measuring {file_type} file validation: {file_path}")
        
        start_time = time.time()
        is_valid, error_msg = self.audio_processor.validate_file(file_path)
        validation_time = time.time() - start_time
        
        result = {
            "success": is_valid,
            "time": validation_time,
            "error": error_msg if not is_valid else None
        }
        
        print(f"✅ {file_type} validation: {validation_time:.3f}s")
        return result
    
    def measure_audio_preparation(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """Measure audio preparation timing using optimized preprocessing"""
        print(f"🎵 Measuring {file_type} audio preparation: {file_path}")
        
        start_time = time.time()
        success, audio_path = self.audio_processor.prepare_audio_for_whisper_fast(file_path)
        preparation_time = time.time() - start_time
        
        result = {
            "success": success,
            "time": preparation_time,
            "audio_path": audio_path if success else None,
            "error": audio_path if not success else None,
            "optimized": True
        }
        
        print(f"✅ {file_type} optimized audio preparation: {preparation_time:.3f}s")
        return result
    
    def measure_transcription(self, audio_path: str, file_type: str, model: str = "base") -> Dict[str, Any]:
        """Measure transcription timing"""
        print(f"🎤 Measuring {file_type} transcription with model: {model}")
        
        start_time = time.time()
        result = self.transcriber.transcribe_audio(
            audio_path=audio_path,
            language=None,  # Auto-detect
            task="transcribe",
            model=model
        )
        transcription_time = time.time() - start_time
        
        timing_result = {
            "success": result.get("success", False),
            "time": transcription_time,
            "text_length": len(result.get("text", "")),
            "segments_count": len(result.get("segments", [])),
            "model_used": result.get("model_used", model),
            "language": result.get("language", "auto"),
            "confidence": result.get("confidence", 0.0),
            "error": result.get("error") if not result.get("success", False) else None,
            "text": result.get("text", ""),
            "segments": result.get("segments", [])
        }
        
        print(f"✅ {file_type} transcription: {transcription_time:.3f}s ({timing_result['segments_count']} segments)")
        return timing_result
    
    def measure_transcription_parallel(self, files: List[Tuple[str, str]], model: str = "base") -> Dict[str, Any]:
        """
        Measure parallel transcription timing for multiple files
        
        Args:
            files: List of tuples (file_path, file_type)
            model: Model to use for transcription
            
        Returns:
            Dictionary with parallel transcription results
        """
        print(f"🎤 Measuring parallel transcription for {len(files)} files with model: {model}")
        
        start_time = time.time()
        results = {}
        
        try:
            # Use ThreadPoolExecutor for parallel processing
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(files)) as executor:
                # Submit transcription tasks
                future_to_file = {}
                for file_path, file_type in files:
                    # Prepare audio first using optimized preprocessing
                    success, audio_path = self.audio_processor.prepare_audio_for_whisper_fast(file_path)
                    if not success:
                        results[file_type] = {
                            "success": False,
                            "error": f"Audio preparation failed: {audio_path}"
                        }
                        continue
                    
                    # Submit transcription task
                    future = executor.submit(
                        self.transcriber.transcribe_audio,
                        audio_path=audio_path,
                        language=None,
                        task="transcribe",
                        model=model
                    )
                    future_to_file[future] = (file_type, file_path)
                
                # Collect results
                for future in concurrent.futures.as_completed(future_to_file):
                    file_type, file_path = future_to_file[future]
                    try:
                        result = future.result()
                        results[file_type] = result
                    except Exception as e:
                        results[file_type] = {
                            "success": False,
                            "error": f"Transcription failed: {str(e)}"
                        }
            
            total_time = time.time() - start_time
            
            # Calculate summary statistics
            successful_transcriptions = sum(1 for r in results.values() if r.get("success", False))
            total_segments = sum(len(r.get("segments", [])) for r in results.values() if r.get("success", False))
            total_text_length = sum(len(r.get("text", "")) for r in results.values() if r.get("success", False))
            
            parallel_result = {
                "success": successful_transcriptions == len(files),
                "time": total_time,
                "files_processed": len(files),
                "successful_transcriptions": successful_transcriptions,
                "total_segments": total_segments,
                "total_text_length": total_text_length,
                "model_used": model,
                "individual_results": results
            }
            
            print(f"✅ Parallel transcription: {total_time:.3f}s ({successful_transcriptions}/{len(files)} successful)")
            return parallel_result
            
        except Exception as e:
            return {
                "success": False,
                "time": time.time() - start_time,
                "error": f"Parallel transcription failed: {str(e)}",
                "files_processed": len(files),
                "successful_transcriptions": 0
            }
    
    def measure_clear_embeddings(self) -> Dict[str, Any]:
        """Measure clear embeddings timing"""
        print(f"🗑️ Measuring clear embeddings")
        
        start_time = time.time()
        success = self.vector_store.clear_existing_embeddings()
        clear_time = time.time() - start_time
        
        result = {
            "success": success,
            "time": clear_time,
            "error": None if success else "Failed to clear embeddings"
        }
        
        print(f"✅ Clear embeddings: {clear_time:.3f}s")
        return result
    
    def measure_chunking(self, transcription_data: Dict[str, Any], file_type: str) -> Dict[str, Any]:
        """Measure chunking timing"""
        print(f"📦 Measuring {file_type} chunking")
        
        start_time = time.time()
        chunks = self.vector_store._generate_chunks(transcription_data, {})
        chunking_time = time.time() - start_time
        
        # Analyze chunk characteristics
        chunk_sizes = [len(chunk.get("text", "")) for chunk in chunks]
        total_chars = sum(chunk_sizes)
        avg_chunk_size = total_chars / len(chunks) if chunks else 0
        
        result = {
            "success": True,
            "time": chunking_time,
            "chunks_count": len(chunks),
            "total_chars": total_chars,
            "avg_chunk_size": avg_chunk_size,
            "min_chunk_size": min(chunk_sizes) if chunk_sizes else 0,
            "max_chunk_size": max(chunk_sizes) if chunk_sizes else 0
        }
        
        print(f"✅ {file_type} chunking: {chunking_time:.3f}s ({len(chunks)} chunks)")
        return result
    
    def measure_embedding_generation(self, chunks: List[Dict[str, Any]], file_type: str) -> Dict[str, Any]:
        """Measure embedding generation timing using batch processing"""
        print(f"🧠 Measuring {file_type} batch embedding generation for {len(chunks)} chunks")
        
        start_time = time.time()
        
        # Get all chunk texts for batch embedding
        chunk_texts = [chunk.get("text", "") for chunk in chunks if chunk.get("text", "")]
        
        # Generate embeddings in batch
        embeddings = self.vector_store.get_embeddings_batch(chunk_texts)
        
        total_time = time.time() - start_time
        successful_embeddings = sum(1 for emb in embeddings if emb is not None)
        failed_embeddings = len(embeddings) - successful_embeddings
        
        # Calculate average time per embedding (total time / number of embeddings)
        avg_embedding_time = total_time / len(embeddings) if embeddings else 0
        
        result = {
            "success": successful_embeddings > 0,
            "time": total_time,
            "successful_embeddings": successful_embeddings,
            "failed_embeddings": failed_embeddings,
            "total_chunks": len(chunks),
            "avg_embedding_time": avg_embedding_time,
            "batch_size": len(chunk_texts)
        }
        
        print(f"✅ {file_type} batch embedding generation: {total_time:.3f}s ({successful_embeddings} successful)")
        return result
    
    def measure_pinecone_upsert(self, chunks: List[Dict[str, Any]], file_type: str) -> Dict[str, Any]:
        """Measure Pinecone upsert timing"""
        print(f"💾 Measuring {file_type} Pinecone upsert for {len(chunks)} chunks")
        
        start_time = time.time()
        
        # Prepare vectors for storage using batch embedding
        vectors_to_upsert = []
        
        # Get all chunk texts for batch embedding
        chunk_texts = [chunk.get("text", "") for chunk in chunks if chunk.get("text", "")]
        
        # Generate embeddings in batch
        embeddings = self.vector_store.get_embeddings_batch(chunk_texts)
        
        # Create vector records
        for chunk, embedding in zip(chunks, embeddings):
            if embedding:
                vector_record = {
                    "id": chunk["id"],
                    "values": embedding,
                    "metadata": chunk["metadata"]
                }
                vectors_to_upsert.append(vector_record)
        
        # Measure actual Pinecone upsert
        upsert_start = time.time()
        if vectors_to_upsert:
            # Get index
            if self.vector_store.index_name not in self.vector_store.client.list_indexes().names():
                return {
                    "success": False,
                    "time": time.time() - start_time,
                    "error": f"Index '{self.vector_store.index_name}' not found"
                }
            
            self.vector_store.index = self.vector_store.client.Index(self.vector_store.index_name)
            
            # Upsert in batches
            batch_size = 100
            total_upsert_time = 0
            batch_times = []
            
            for i in range(0, len(vectors_to_upsert), batch_size):
                batch = vectors_to_upsert[i:i + batch_size]
                batch_start = time.time()
                self.vector_store.index.upsert(vectors=batch)
                batch_time = time.time() - batch_start
                batch_times.append(batch_time)
                total_upsert_time += batch_time
            
            total_time = time.time() - start_time
            
            return {
                "success": True,
                "time": total_time,
                "vectors_stored": len(vectors_to_upsert),
                "batches_processed": len(batch_times),
                "total_upsert_time": total_upsert_time,
                "avg_batch_time": sum(batch_times) / len(batch_times) if batch_times else 0,
                "batch_embedding_used": True
            }
        else:
            return {
                "success": False,
                "time": time.time() - start_time,
                "error": "No valid vectors to store"
            }
    
    def measure_indexing_wait(self, chunks: List[Dict[str, Any]], file_type: str) -> Dict[str, Any]:
        """Measure Pinecone indexing wait timing"""
        print(f"⏳ Measuring {file_type} indexing wait")
        
        start_time = time.time()
        
        # Get first chunk ID for testing
        first_id = None
        if chunks:
            first_id = chunks[0]["id"]
        
        indexing_wait_time = 0
        if first_id:
            # Wait for indexing
            indexing_wait_time = 0  # We'll measure this separately
            success = self.vector_store._wait_for_indexing(test_id=first_id, max_retries=10, base_delay=1.0)
            indexing_wait_time = time.time() - start_time
        
        result = {
            "success": True,
            "time": indexing_wait_time,
            "indexing_success": success if first_id else False
        }
        
        print(f"✅ {file_type} indexing wait: {indexing_wait_time:.3f}s")
        return result
    
    def measure_vector_search(self, secondary_transcription: Dict[str, Any], threshold: float = 0.7) -> Dict[str, Any]:
        """Measure vector search timing"""
        print(f"🔍 Measuring vector search with threshold: {threshold}")
        
        start_time = time.time()
        
        # Step 1: Secondary text extraction
        text_extraction_start = time.time()
        secondary_text = secondary_transcription.get("text", "").strip()
        if not secondary_text:
            return {
                "success": False,
                "total_time": time.time() - start_time,
                "error": "No text found in secondary transcription"
            }
        text_extraction_time = time.time() - text_extraction_start
        
        # Step 2: Dynamic threshold adjustment
        threshold_start = time.time()
        secondary_length = len(secondary_text)
        if secondary_length < 100:
            adjusted_threshold = 0.5
        elif secondary_length > 500:
            adjusted_threshold = 0.3
        else:
            adjusted_threshold = threshold
        threshold_time = time.time() - threshold_start
        
        # Step 3: Secondary text chunking
        chunking_start = time.time()
        secondary_chunks = self.vector_store._chunk_secondary_text(secondary_transcription)
        chunking_time = time.time() - chunking_start
        
        # Step 4: Vector search for each chunk
        search_start = time.time()
        all_matches = []
        total_confidence = 0.0
        chunk_search_times = []
        
        for chunk_idx, chunk in enumerate(secondary_chunks):
            chunk_text = chunk.get("text", "").strip()
            if not chunk_text:
                continue
            
            chunk_search_start = time.time()
            chunk_matches = self.vector_store._search_single_chunk(chunk_text, adjusted_threshold)
            chunk_search_time = time.time() - chunk_search_start
            chunk_search_times.append(chunk_search_time)
            
            # Content overlap checking
            for match in chunk_matches:
                confidence = getattr(match, 'score', 0.0)
                metadata = getattr(match, 'metadata', {})
                match_text = metadata.get("text", "")
                has_content_overlap = self.vector_store._check_content_overlap(chunk_text, match_text)
                
                if has_content_overlap:
                    all_matches.append({
                        "start_time": metadata.get("start_time", 0.0),
                        "end_time": metadata.get("end_time", 0.0),
                        "text": match_text,
                        "confidence": confidence,
                        "segment_index": metadata.get("segment_index", 0)
                    })
                    total_confidence += confidence
        
        search_time = time.time() - search_start
        
        # Step 5: Match merging
        merging_start = time.time()
        merged_matches = self.vector_store._merge_overlapping_matches(all_matches)
        merging_time = time.time() - merging_start
        
        total_time = time.time() - start_time
        avg_confidence = total_confidence / len(all_matches) if all_matches else 0.0
        
        return {
            "success": True,
            "total_time": total_time,
            "text_extraction_time": text_extraction_time,
            "threshold_adjustment_time": threshold_time,
            "chunking_time": chunking_time,
            "search_time": search_time,
            "merging_time": merging_time,
            "chunks_processed": len(secondary_chunks),
            "total_matches_found": len(all_matches),
            "unique_matches_after_merge": len(merged_matches),
            "avg_confidence": avg_confidence,
            "adjusted_threshold": adjusted_threshold,
            "avg_chunk_search_time": sum(chunk_search_times) / len(chunk_search_times) if chunk_search_times else 0.0
        }
    
    async def measure_complete_comparison_workflow(self, primary_file: str, secondary_file: str, model: str = "base", threshold: float = 0.7) -> Dict[str, Any]:
        """Measure the complete comparison workflow timing"""
        print(f"🚀 Starting complete comparison workflow timing")
        print(f"📁 Primary file: {primary_file}")
        print(f"📁 Secondary file: {secondary_file}")
        print(f"🤖 Model: {model}")
        print(f"🎯 Threshold: {threshold}")
        
        workflow_start = time.time()
        workflow_results = {
            "primary_file": primary_file,
            "secondary_file": secondary_file,
            "model": model,
            "threshold": threshold,
            "phases": {
                "primary_storage": {},
                "secondary_comparison": {}
            },
            "total_time": 0.0
        }
        
        # ===== PHASE 1: PRIMARY STORAGE =====
        print(f"\n📦 PHASE 1: PRIMARY STORAGE")
        print("=" * 50)
        
        # Step 1: Primary file validation
        workflow_results["phases"]["primary_storage"]["validation"] = self.measure_file_validation(primary_file, "primary")
        if not workflow_results["phases"]["primary_storage"]["validation"]["success"]:
            workflow_results["total_time"] = time.time() - workflow_start
            return workflow_results
        
        # Step 2: Primary audio preparation
        workflow_results["phases"]["primary_storage"]["audio_preparation"] = self.measure_audio_preparation(primary_file, "primary")
        if not workflow_results["phases"]["primary_storage"]["audio_preparation"]["success"]:
            workflow_results["total_time"] = time.time() - workflow_start
            return workflow_results
        
        # Step 3: Primary transcription
        workflow_results["phases"]["primary_storage"]["transcription"] = self.measure_transcription(
            workflow_results["phases"]["primary_storage"]["audio_preparation"]["audio_path"], 
            "primary", model
        )
        if not workflow_results["phases"]["primary_storage"]["transcription"]["success"]:
            workflow_results["total_time"] = time.time() - workflow_start
            return workflow_results
        
        # Step 4: Clear existing embeddings
        workflow_results["phases"]["primary_storage"]["clear_embeddings"] = self.measure_clear_embeddings()
        
        # Step 5: Primary chunking
        primary_transcription_data = {
            "text": workflow_results["phases"]["primary_storage"]["transcription"]["text"],
            "segments": workflow_results["phases"]["primary_storage"]["transcription"]["segments"]
        }
        workflow_results["phases"]["primary_storage"]["chunking"] = self.measure_chunking(primary_transcription_data, "primary")
        
        # Step 6: Primary embedding generation
        primary_chunks = self.vector_store._generate_chunks(primary_transcription_data, {})
        workflow_results["phases"]["primary_storage"]["embedding_generation"] = self.measure_embedding_generation(primary_chunks, "primary")
        
        # Step 7: Primary Pinecone upsert
        workflow_results["phases"]["primary_storage"]["pinecone_upsert"] = self.measure_pinecone_upsert(primary_chunks, "primary")
        
        # Step 8: Primary indexing wait
        workflow_results["phases"]["primary_storage"]["indexing_wait"] = self.measure_indexing_wait(primary_chunks, "primary")
        
        # ===== PHASE 2: SECONDARY COMPARISON =====
        print(f"\n🔍 PHASE 2: SECONDARY COMPARISON")
        print("=" * 50)
        
        # Step 1: Secondary file validation
        workflow_results["phases"]["secondary_comparison"]["validation"] = self.measure_file_validation(secondary_file, "secondary")
        if not workflow_results["phases"]["secondary_comparison"]["validation"]["success"]:
            workflow_results["total_time"] = time.time() - workflow_start
            return workflow_results
        
        # Step 2: Secondary audio preparation
        workflow_results["phases"]["secondary_comparison"]["audio_preparation"] = self.measure_audio_preparation(secondary_file, "secondary")
        if not workflow_results["phases"]["secondary_comparison"]["audio_preparation"]["success"]:
            workflow_results["total_time"] = time.time() - workflow_start
            return workflow_results
        
        # Step 3: Secondary transcription
        workflow_results["phases"]["secondary_comparison"]["transcription"] = self.measure_transcription(
            workflow_results["phases"]["secondary_comparison"]["audio_preparation"]["audio_path"], 
            "secondary", model
        )
        if not workflow_results["phases"]["secondary_comparison"]["transcription"]["success"]:
            workflow_results["total_time"] = time.time() - workflow_start
            return workflow_results
        
        # Step 4: Vector search (comparison)
        secondary_transcription_data = {
            "text": workflow_results["phases"]["secondary_comparison"]["transcription"]["text"],
            "segments": workflow_results["phases"]["secondary_comparison"]["transcription"]["segments"]
        }
        workflow_results["phases"]["secondary_comparison"]["vector_search"] = self.measure_vector_search(secondary_transcription_data, threshold)
        
        workflow_results["total_time"] = time.time() - workflow_start
        
        print(f"\n🎉 Complete workflow completed in {workflow_results['total_time']:.3f}s")
        return workflow_results
    
    async def measure_complete_comparison_workflow_parallel(self, primary_file: str, secondary_file: str, model: str = "base", threshold: float = 0.7) -> Dict[str, Any]:
        """Measure the complete comparison workflow timing with parallel transcription"""
        print(f"🚀 Starting parallel comparison workflow timing")
        print(f"📁 Primary file: {primary_file}")
        print(f"📁 Secondary file: {secondary_file}")
        print(f"🤖 Model: {model}")
        print(f"🎯 Threshold: {threshold}")
        
        workflow_start = time.time()
        workflow_results = {
            "primary_file": primary_file,
            "secondary_file": secondary_file,
            "model": model,
            "threshold": threshold,
            "phases": {
                "parallel_transcription": {},
                "primary_storage": {},
                "secondary_comparison": {}
            },
            "total_time": 0.0,
            "parallel_processing": True
        }
        
        # ===== PHASE 1: PARALLEL TRANSCRIPTION =====
        print(f"\n🎤 PHASE 1: PARALLEL TRANSCRIPTION")
        print("=" * 50)
        
        # Validate both files first
        primary_valid = self.measure_file_validation(primary_file, "primary")
        secondary_valid = self.measure_file_validation(secondary_file, "secondary")
        
        if not primary_valid["success"] or not secondary_valid["success"]:
            workflow_results["total_time"] = time.time() - workflow_start
            return workflow_results
        
        # Prepare audio for both files
        primary_audio = self.measure_audio_preparation(primary_file, "primary")
        secondary_audio = self.measure_audio_preparation(secondary_file, "secondary")
        
        if not primary_audio["success"] or not secondary_audio["success"]:
            workflow_results["total_time"] = time.time() - workflow_start
            return workflow_results
        
        # Parallel transcription
        files_to_transcribe = [
            (primary_audio["audio_path"], "primary"),
            (secondary_audio["audio_path"], "secondary")
        ]
        
        parallel_result = self.measure_transcription_parallel(files_to_transcribe, model)
        workflow_results["phases"]["parallel_transcription"] = parallel_result
        
        if not parallel_result["success"]:
            workflow_results["total_time"] = time.time() - workflow_start
            return workflow_results
        
        # Extract individual results
        individual_results = parallel_result["individual_results"]
        primary_transcription = individual_results["primary"]
        secondary_transcription = individual_results["secondary"]
        
        # ===== PHASE 2: PRIMARY STORAGE =====
        print(f"\n📦 PHASE 2: PRIMARY STORAGE")
        print("=" * 50)
        
        # Clear existing embeddings
        workflow_results["phases"]["primary_storage"] = {}
        workflow_results["phases"]["primary_storage"]["clear_embeddings"] = self.measure_clear_embeddings()
        
        # Primary chunking
        primary_transcription_data = {
            "text": primary_transcription["text"],
            "segments": primary_transcription["segments"]
        }
        workflow_results["phases"]["primary_storage"]["chunking"] = self.measure_chunking(primary_transcription_data, "primary")
        
        # Primary embedding generation
        primary_chunks = self.vector_store._generate_chunks(primary_transcription_data, {})
        workflow_results["phases"]["primary_storage"]["embedding_generation"] = self.measure_embedding_generation(primary_chunks, "primary")
        
        # Primary Pinecone upsert
        workflow_results["phases"]["primary_storage"]["pinecone_upsert"] = self.measure_pinecone_upsert(primary_chunks, "primary")
        
        # Primary indexing wait
        workflow_results["phases"]["primary_storage"]["indexing_wait"] = self.measure_indexing_wait(primary_chunks, "primary")
        
        # ===== PHASE 3: SECONDARY COMPARISON =====
        print(f"\n🔍 PHASE 3: SECONDARY COMPARISON")
        print("=" * 50)
        
        # Vector search (comparison)
        secondary_transcription_data = {
            "text": secondary_transcription["text"],
            "segments": secondary_transcription["segments"]
        }
        workflow_results["phases"]["secondary_comparison"] = {}
        workflow_results["phases"]["secondary_comparison"]["vector_search"] = self.measure_vector_search(secondary_transcription_data, threshold)
        
        workflow_results["total_time"] = time.time() - workflow_start
        
        print(f"\n🎉 Parallel workflow completed in {workflow_results['total_time']:.3f}s")
        return workflow_results
    
    def print_comprehensive_timing_summary(self, results: Dict[str, Any]):
        """Print a comprehensive timing summary"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE COMPARISON WORKFLOW TIMING SUMMARY")
        print("="*80)
        
        print(f"📁 Primary file: {results['primary_file']}")
        print(f"📁 Secondary file: {results['secondary_file']}")
        print(f"🤖 Model: {results['model']}")
        print(f"🎯 Threshold: {results['threshold']}")
        print(f"⏱️  Total time: {results['total_time']:.3f}s")
        
        # Show optimizations used
        if results.get('parallel_processing', False):
            print("🚀 Optimizations: Batch Embedding + Model Caching + Audio Optimization + Parallel Processing")
        else:
            print("🚀 Optimizations: Batch Embedding + Model Caching + Audio Optimization")
        print()
        
        # Calculate phase breakdown
        phases = results.get("phases", {})
        phase_times = {}
        total_phase_time = 0.0
        
        for phase_name, phase_steps in phases.items():
            phase_total = 0.0
            for step_name, step_result in phase_steps.items():
                if step_result.get("success", False):
                    step_time = step_result.get("time", 0.0)
                    phase_total += step_time
            phase_times[phase_name] = phase_total
            total_phase_time += phase_total
        
        # Sort phases by time
        sorted_phases = sorted(phase_times.items(), key=lambda x: x[1], reverse=True)
        
        print("📈 PHASE BREAKDOWN (by time):")
        print("-" * 60)
        for phase_name, phase_time in sorted_phases:
            percentage = (phase_time / total_phase_time * 100) if total_phase_time > 0 else 0
            print(f"  {phase_name.replace('_', ' ').title():<25} {phase_time:>8.3f}s ({percentage:>5.1f}%)")
        
        print("-" * 60)
        print(f"  {'Total Phases':<25} {total_phase_time:>8.3f}s")
        print(f"  {'Overhead/Other':<25} {(results['total_time'] - total_phase_time):>8.3f}s")
        print()
        
        # Detailed breakdown for each phase
        for phase_name, phase_steps in phases.items():
            print(f"🔍 {phase_name.replace('_', ' ').upper()} DETAILED BREAKDOWN:")
            print("-" * 50)
            
            step_times = {}
            for step_name, step_result in phase_steps.items():
                if step_result.get("success", False):
                    step_time = step_result.get("time", 0.0)
                    step_times[step_name] = step_time
            
            # Sort steps by time
            sorted_steps = sorted(step_times.items(), key=lambda x: x[1], reverse=True)
            
            for step_name, step_time in sorted_steps:
                percentage = (step_time / sum(step_times.values()) * 100) if step_times else 0
                print(f"  {step_name.replace('_', ' ').title():<25} {step_time:>8.3f}s ({percentage:>5.1f}%)")
            
            # Additional metrics for each phase
            if phase_name == "primary_storage":
                if "transcription" in phase_steps:
                    trans = phase_steps["transcription"]
                    print(f"    📝 Text length: {trans.get('text_length', 0):,} chars")
                    print(f"    📝 Segments: {trans.get('segments_count', 0)}")
                
                if "chunking" in phase_steps:
                    chunk = phase_steps["chunking"]
                    print(f"    📦 Chunks: {chunk.get('chunks_count', 0)}")
                    print(f"    📦 Avg chunk size: {chunk.get('avg_chunk_size', 0):.1f} chars")
                
                if "embedding_generation" in phase_steps:
                    emb = phase_steps["embedding_generation"]
                    print(f"    🧠 Successful embeddings: {emb.get('successful_embeddings', 0)}")
                    print(f"    🧠 Avg embedding time: {emb.get('avg_embedding_time', 0):.3f}s")
                
                if "pinecone_upsert" in phase_steps:
                    storage = phase_steps["pinecone_upsert"]
                    print(f"    💾 Vectors stored: {storage.get('vectors_stored', 0)}")
                    print(f"    💾 Batches processed: {storage.get('batches_processed', 0)}")
            
            elif phase_name == "secondary_comparison":
                if "transcription" in phase_steps:
                    trans = phase_steps["transcription"]
                    print(f"    📝 Text length: {trans.get('text_length', 0):,} chars")
                    print(f"    📝 Segments: {trans.get('segments_count', 0)}")
                
                if "vector_search" in phase_steps:
                    search = phase_steps["vector_search"]
                    print(f"    🔍 Chunks processed: {search.get('chunks_processed', 0)}")
                    print(f"    🔍 Total matches: {search.get('total_matches_found', 0)}")
                    print(f"    🔍 Unique matches: {search.get('unique_matches_after_merge', 0)}")
                    print(f"    🔍 Avg confidence: {search.get('avg_confidence', 0):.3f}")
            
            print()
        
        print("="*80)


async def main():
    """Main function to run comprehensive timing analysis"""
    if len(sys.argv) < 3:
        print("Usage: python test_comprehensive_comparison_timing.py <primary_file> <secondary_file> [model] [threshold]")
        print("Example: python test_comprehensive_comparison_timing.py primary.mp3 secondary.mp3 base 0.7")
        sys.exit(1)
    
    primary_file = sys.argv[1]
    secondary_file = sys.argv[2]
    model = sys.argv[3] if len(sys.argv) > 3 else "base"
    threshold = float(sys.argv[4]) if len(sys.argv) > 4 else 0.7
    
    # Validate files exist
    if not os.path.exists(primary_file):
        print(f"❌ Primary file not found: {primary_file}")
        sys.exit(1)
    
    if not os.path.exists(secondary_file):
        print(f"❌ Secondary file not found: {secondary_file}")
        sys.exit(1)
    
    # Run timing analysis with all optimizations
    analyzer = ComprehensiveComparisonTimingAnalyzer()
    
    # Use parallel workflow for better performance
    print("🚀 Using optimized workflow with all improvements:")
    print("   ✅ Batch Embedding Generation")
    print("   ✅ Model Caching")
    print("   ✅ Audio Preprocessing Optimization")
    print("   ✅ Parallel Processing")
    print()
    
    results = await analyzer.measure_complete_comparison_workflow_parallel(primary_file, secondary_file, model, threshold)
    
    # Print summary
    analyzer.print_comprehensive_timing_summary(results)
    
    # Save results to file
    output_file = f"comprehensive_comparison_timing_results_{int(time.time())}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"💾 Detailed results saved to: {output_file}")


if __name__ == "__main__":
    asyncio.run(main()) 
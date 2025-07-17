"""
Output formatting utilities for Whisper AI Transcription Project
"""

import json
from pathlib import Path
from typing import Dict, Any, Union
import config


class OutputFormatter:
    """Handles formatting and output of transcription results"""
    
    def __init__(self):
        self.supported_formats = config.OUTPUT_FORMATS
        self.default_format = config.DEFAULT_OUTPUT_FORMAT
    
    def format_transcription_result(self, result: Dict[str, Any], 
                                  output_format: str = None) -> str:
        """
        Format transcription result in the specified format
        
        Args:
            result: Transcription result dictionary
            output_format: Desired output format (txt, json, srt)
            
        Returns:
            Formatted string output
        """
        output_format = output_format or self.default_format
        
        if output_format not in self.supported_formats:
            output_format = self.default_format
        
        if output_format == "json":
            return self._format_json(result)
        elif output_format == "srt":
            return self._format_srt(result)
        else:  # txt format
            return self._format_txt(result)
    
    def _format_txt(self, result: Dict[str, Any]) -> str:
        """Format result as plain text"""
        if not result.get("success", False):
            return f"Error: {result.get('error', 'Unknown error')}"
        
        output_lines = []
        
        # Add header information
        output_lines.append("=" * 50)
        output_lines.append("WHISPER TRANSCRIPTION RESULTS")
        output_lines.append("=" * 50)
        output_lines.append(f"File: {result.get('file_path', 'Unknown')}")
        output_lines.append(f"Model: {result.get('model_used', 'Unknown')}")
        output_lines.append(f"Language: {result.get('language', 'Unknown')}")
        output_lines.append(f"Processing Time: {result.get('processing_time', 0):.2f} seconds")
        output_lines.append(f"Task: {result.get('task', 'transcribe')}")
        output_lines.append("")
        
        # Add transcription text
        output_lines.append("TRANSCRIPTION:")
        output_lines.append("-" * 20)
        output_lines.append(result.get("text", "No transcription available"))
        output_lines.append("")
        
        # Add segments if available
        segments = result.get("segments", [])
        if segments:
            output_lines.append("SEGMENTS:")
            output_lines.append("-" * 20)
            for i, segment in enumerate(segments, 1):
                start_time = segment.get("start", 0)
                end_time = segment.get("end", 0)
                text = segment.get("text", "").strip()
                
                output_lines.append(f"[{start_time:.2f}s - {end_time:.2f}s] {text}")
        
        return "\n".join(output_lines)
    
    def _format_json(self, result: Dict[str, Any]) -> str:
        """Format result as JSON"""
        # Create a clean JSON structure
        json_result = {
            "success": result.get("success", False),
            "file_path": result.get("file_path", ""),
            "model_used": result.get("model_used", ""),
            "language": result.get("language", ""),
            "processing_time": result.get("processing_time", 0),
            "task": result.get("task", "transcribe"),
            "text": result.get("text", ""),
            "segments": result.get("segments", [])
        }
        
        if not result.get("success", False):
            json_result["error"] = result.get("error", "Unknown error")
        
        return json.dumps(json_result, indent=2, ensure_ascii=False)
    
    def _format_srt(self, result: Dict[str, Any]) -> str:
        """Format result as SRT subtitle format"""
        if not result.get("success", False):
            return f"Error: {result.get('error', 'Unknown error')}"
        
        segments = result.get("segments", [])
        if not segments:
            return "No segments available for SRT format"
        
        srt_lines = []
        
        for i, segment in enumerate(segments, 1):
            start_time = segment.get("start", 0)
            end_time = segment.get("end", 0)
            text = segment.get("text", "").strip()
            
            # Convert seconds to SRT time format (HH:MM:SS,mmm)
            start_str = self._seconds_to_srt_time(start_time)
            end_str = self._seconds_to_srt_time(end_time)
            
            srt_lines.append(str(i))
            srt_lines.append(f"{start_str} --> {end_str}")
            srt_lines.append(text)
            srt_lines.append("")  # Empty line between subtitles
        
        return "\n".join(srt_lines)
    
    def _seconds_to_srt_time(self, seconds: float) -> str:
        """Convert seconds to SRT time format (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
    
    def save_output(self, result: Dict[str, Any], 
                   output_path: Union[str, Path],
                   output_format: str = None) -> bool:
        """
        Save transcription result to file
        
        Args:
            result: Transcription result dictionary
            output_path: Path to save the output file
            output_format: Output format (txt, json, srt)
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            output_path = Path(output_path)
            
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Format the result
            formatted_output = self.format_transcription_result(result, output_format)
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(formatted_output)
            
            print(f"Output saved to: {output_path}")
            return True
            
        except Exception as e:
            print(f"Error saving output: {str(e)}")
            return False
    
    def print_summary(self, result: Dict[str, Any]) -> None:
        """
        Print a summary of the transcription result
        
        Args:
            result: Transcription result dictionary
        """
        if not result.get("success", False):
            print(f"❌ Transcription failed: {result.get('error', 'Unknown error')}")
            return
        
        print("\n" + "=" * 50)
        print("TRANSCRIPTION SUMMARY")
        print("=" * 50)
        print(f"✅ Success: {result.get('file_path', 'Unknown')}")
        print(f"📝 Model: {result.get('model_used', 'Unknown')}")
        print(f"🌍 Language: {result.get('language', 'Unknown')}")
        print(f"⏱️  Processing Time: {result.get('processing_time', 0):.2f} seconds")
        print(f"📊 Task: {result.get('task', 'transcribe')}")
        
        text = result.get("text", "")
        if text:
            word_count = len(text.split())
            char_count = len(text)
            print(f"📄 Text Length: {word_count} words, {char_count} characters")
        
        segments = result.get("segments", [])
        if segments:
            print(f"🎬 Segments: {len(segments)}")
        
        print("=" * 50) 
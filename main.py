"""
Main entry point for Whisper AI Transcription Project
"""

import argparse
import sys
from pathlib import Path
from src.audio_processor import AudioProcessor
from src.transcriber import WhisperTranscriber
from src.output_formatter import OutputFormatter
import config


def main():
    """Main function for CLI interface"""
    parser = argparse.ArgumentParser(
        description="Whisper AI Transcription Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py audio.mp3
  python main.py video.mp4 --model base --output-format json
  python main.py audio.wav --language en --task translate
        """
    )
    
    # Required arguments
    parser.add_argument(
        "file_path",
        help="Path to the audio or video file to transcribe"
    )
    
    # Optional arguments
    parser.add_argument(
        "--model",
        choices=config.AVAILABLE_MODELS,
        default=config.DEFAULT_MODEL,
        help=f"Whisper model to use (default: {config.DEFAULT_MODEL})"
    )
    
    parser.add_argument(
        "--language",
        default=config.DEFAULT_LANGUAGE,
        help="Language code for transcription (default: auto-detect)"
    )
    
    parser.add_argument(
        "--task",
        choices=["transcribe", "translate"],
        default="transcribe",
        help="Task type: transcribe or translate (default: transcribe)"
    )
    
    parser.add_argument(
        "--output-format",
        choices=config.OUTPUT_FORMATS,
        default=config.DEFAULT_OUTPUT_FORMAT,
        help=f"Output format (default: {config.DEFAULT_OUTPUT_FORMAT})"
    )
    
    parser.add_argument(
        "--output-file",
        help="Output file path (default: auto-generated)"
    )
    
    parser.add_argument(
        "--detect-language-only",
        action="store_true",
        help="Only detect language, don't transcribe"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Initialize components
    audio_processor = AudioProcessor()
    transcriber = WhisperTranscriber(model_name=args.model)
    output_formatter = OutputFormatter()
    
    # Validate input file
    print(f"🔍 Validating file: {args.file_path}")
    is_valid, error_msg = audio_processor.validate_file(args.file_path)
    
    if not is_valid:
        print(f"❌ File validation failed: {error_msg}")
        sys.exit(1)
    
    print("✅ File validation passed")
    
    # Get file information
    file_info = audio_processor.get_file_info(args.file_path)
    if args.verbose:
        print(f"📁 File info: {file_info}")
    
    # Prepare audio for transcription
    print("🎵 Preparing audio for transcription...")
    success, audio_path = audio_processor.prepare_audio_for_whisper_fast(args.file_path)
    
    if not success:
        print(f"❌ Audio preparation failed: {audio_path}")
        sys.exit(1)
    
    print(f"✅ Audio prepared: {audio_path}")
    
    # Language detection only
    if args.detect_language_only:
        print("🌍 Detecting language...")
        language_result = transcriber.detect_language(audio_path)
        
        if language_result.get("success", False):
            detected_lang = language_result["detected_language"]
            print(f"✅ Detected language: {detected_lang}")
            
            if args.verbose:
                probs = language_result.get("language_probabilities", {})
                print("Language probabilities:")
                for lang, prob in sorted(probs.items(), key=lambda x: x[1], reverse=True)[:5]:
                    print(f"  {lang}: {prob:.3f}")
        else:
            print(f"❌ Language detection failed: {language_result.get('error', 'Unknown error')}")
            sys.exit(1)
        
        return
    
    # Perform transcription
    print(f"🎤 Starting transcription with model: {args.model}")
    result = transcriber.transcribe_audio(
        audio_path=audio_path,
        language=args.language if args.language != "auto" else None,
        task=args.task
    )
    
    # Handle transcription result
    if not result.get("success", False):
        print(f"❌ Transcription failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)
    
    # Print summary
    output_formatter.print_summary(result)
    
    # Save output if requested
    if args.output_file:
        output_path = Path(args.output_file)
        success = output_formatter.save_output(result, output_path, args.output_format)
        if not success:
            print("❌ Failed to save output file")
            sys.exit(1)
    else:
        # Print formatted output to console
        formatted_output = output_formatter.format_transcription_result(result, args.output_format)
        print("\n" + "=" * 50)
        print("TRANSCRIPTION OUTPUT")
        print("=" * 50)
        print(formatted_output)
    
    print("\n✅ Transcription completed successfully!")


if __name__ == "__main__":
    main() 
"""
Configuration settings for Whisper AI Transcription Project
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supported audio formats
SUPPORTED_AUDIO_FORMATS = ['.mp3', '.wav', '.flac', '.m4a', '.aac']

# Supported video formats (for audio extraction)
SUPPORTED_VIDEO_FORMATS = ['.mp4', '.avi', '.mov', '.mkv']

# Default model to use
DEFAULT_MODEL = 'base'

# Available Whisper models
AVAILABLE_MODELS = ['tiny', 'base', 'small', 'medium', 'large']

# Output formats
OUTPUT_FORMATS = ['txt', 'json', 'srt']

# Default output format
DEFAULT_OUTPUT_FORMAT = 'txt'

# Maximum file size (in MB) - adjust based on available memory
MAX_FILE_SIZE_MB = 500

# Default language for transcription
DEFAULT_LANGUAGE = 'auto'

# Pinecone Configuration
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY', '')
PINECONE_ENVIRONMENT = os.getenv('PINECONE_ENVIRONMENT', 'us-east-1')
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME', 'transcription')

# OpenAI Configuration (for embeddings)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

# Chunking Configuration
CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '1000'))
CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', '200'))

CHUNKING_CONFIG = {
    "segment_based": True,      # Use Whisper segments as primary chunks
    "max_segment_length": 500,  # If segment > 500 chars, split it
    "min_chunk_size": 50,       # Minimum chunk size
    "max_chunk_size": 1000,     # Maximum chunk size
    "overlap_size": 200,        # Overlap between chunks
    "preserve_timestamps": True, # Keep start/end times
    "preserve_context": True     # Maintain segment boundaries
} 
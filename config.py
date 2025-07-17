"""
Configuration settings for Whisper AI Transcription Project
"""

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
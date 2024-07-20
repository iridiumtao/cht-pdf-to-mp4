# Build-in: FileNotFoundError


class InvalidFileError(Exception):
    """Raised when a file is invalid or corrupted."""

    def __init__(self, file_path):
        self.message = f"Invalid or corrupted file: {file_path}"
        super().__init__(self.message)


class OCRProcessingError(Exception):
    """Raised when OCR processing fails."""

    def __init__(self, image_path, error_message):
        self.message = f"OCR processing failed for {image_path}: {error_message}"
        super().__init__(self.message)


class SpeechRecognitionError(Exception):
    """Raised when speech recognition processing fails."""

    def __init__(self, audio_path, error_message):
        self.message = f"Speech recognition failed for {audio_path}: {error_message}"
        super().__init__(self.message)


class TextMatchingError(Exception):
    """Raised when text matching between image and audio fails."""

    def __init__(self, image_text, audio_text):
        self.message = f"Text matching failed between image text and audio text: {image_text} vs {audio_text}"
        super().__init__(self.message)


class VideoCreationError(Exception):
    """Raised when video creation fails."""

    def __init__(self, reason):
        self.message = f"Video creation failed: {reason}"
        super().__init__(self.message)


class AudioVideoSyncError(Exception):
    """Raised when audio and video synchronization fails."""

    def __init__(self, video_length, audio_length):
        self.message = f"Audio and video synchronization failed: Video length ({video_length}s) vs Audio length ({audio_length}s)"
        super().__init__(self.message)


class ConfigurationError(Exception):
    """Raised when there is a configuration error."""

    def __init__(self, config_item):
        self.message = f"Configuration error: Missing or invalid configuration for {config_item}"
        super().__init__(self.message)

import os
import whisper
import logging
from typing import Optional
from functools import lru_cache

# Configure logging
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))
logger = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def load_whisper_model(model_size: str = None):
    """Cache Whisper model to avoid reloading"""
    model_size = model_size or os.getenv('WHISPER_MODEL', 'base')
    logger.info(f"Loading Whisper model: {model_size}")
    try:
        return whisper.load_model(model_size)
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        raise

def transcribe_audio(audio_path: str) -> Optional[str]:
    """Convert audio to text using Whisper"""
    try:
        if not os.path.exists(audio_path):
            logger.error(f"Audio file not found: {audio_path}")
            return None

        logger.info(f"Transcribing audio: {audio_path}")
        model = load_whisper_model()
        
        # Use FP16=False for better CPU compatibility
        result = model.transcribe(
            audio_path,
            fp16=False,
            language='en'  # Set language if known
        )
        
        if not result or 'text' not in result:
            logger.error("Transcription returned no text")
            return None
            
        logger.info("Transcription successful")
        return result['text'].strip()
        
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}", exc_info=True)
        return None
import os
import logging
import requests
import tiktoken
from typing import Optional
from dotenv import load_dotenv

# Configure environment and logging
load_dotenv()
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))
logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """Count tokens for a given text"""
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except:
        # Fallback rough estimation
        return len(text.split()) // 3

def truncate_text(text: str, max_tokens: int = 10000) -> str:
    """Truncate text to stay within token limits"""
    tokens = count_tokens(text)
    if tokens <= max_tokens:
        return text
        
    ratio = max_tokens / tokens
    truncated_length = int(len(text) * ratio)
    return text[:truncated_length] + "... [truncated]"

def summarize_text(text: str) -> Optional[str]:
    """Generate summary using Gemini AI API"""
    try:
        if not text or not GEMINI_API_KEY:
            logger.error("Missing text or API key")
            return None

        response = requests.post(
            "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent",
            params={"key": GEMINI_API_KEY},
            json={
                "contents": [
                    {"parts": [{"text": f"Summarize this in 10 numbered points:\n{text}"}]}
                ]
            }
        )
        response.raise_for_status()
        summary = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        logger.info("Summary generated successfully")
        return summary.strip() if summary else None

    except Exception as e:
        logger.error(f"Summarization failed: {str(e)}", exc_info=True)
        return None
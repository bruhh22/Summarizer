import os
import re
import logging
import yt_dlp
from typing import Optional
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))
logger = logging.getLogger(__name__)

def sanitize_filename(title: str) -> str:
    """Remove invalid characters from filename"""
    return re.sub(r'[\\/*?:"<>|]', "", title).strip()

def validate_youtube_url(url: str) -> bool:
    """Check if URL is a valid YouTube URL"""
    try:
        parsed = urlparse(url)
        return parsed.netloc in ('youtube.com', 'www.youtube.com', 'youtu.be')
    except:
        return False


def download_youtube_audio(url: str, output_dir: str) -> Optional[str]:
    """
    Download audio from YouTube video using yt-dlp.
    Returns path to downloaded audio file or None if failed.
    """
    try:
        if not validate_youtube_url(url):
            logger.error(f"Invalid YouTube URL: {url}")
            return None

        os.makedirs(output_dir, exist_ok=True)
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_dir, '%(title)s_audio.%(ext)s'),
            'quiet': True,
            'noplaylist': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
           info = ydl.extract_info(url, download=True)
           # Get the actual output filename from yt-dlp
           output_path = ydl.prepare_filename(info)
           # If you use FFmpegExtractAudio, change extension to .mp3
           output_path = os.path.splitext(output_path)[0] + ".mp3"
           if os.path.exists(output_path):
              logger.info(f"Audio saved to: {output_path}")
              return output_path
           else:
              logger.error("Audio file not found after download")
              logger.error(f"Tried path: {output_path}")
              logger.error(f"Files in output_dir: {os.listdir(output_dir)}")
              return None

    except Exception as e:
        logger.error(f"Audio download failed: {str(e)}", exc_info=True)
        return None
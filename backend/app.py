import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import logging
from utils.youtube_audio import download_youtube_audio
from utils.transcribe import transcribe_audio
from utils.summarize import summarize_text , truncate_text

# Initialize Flask app
print("Starting app.py")
app = Flask(__name__)
CORS(app, resources={r"/summarize": {"origins": ["http://localhost:8000", "https://summarizer-swart-rho.vercel.app", "https://summarizer-git-master-bruhh22s-projects.vercel.app", "https://summarizer-git-master-bruhh22s-projects.vercel.app/"]}})  # Production CORS

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/summary_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
if not os.getenv("GEMINI_API_KEY"):
    logger.error("GEMINI_API_KEY not found in environment variables")
    raise ValueError("Missing Gemini API key")

# Configuration
UPLOAD_FOLDER = '/tmp/temp_audio'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB limit for audio files

@app.route('/summarize', methods=['POST'])
def summarize():
    try:
        # Validate request
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
            
        data = request.get_json()
        youtube_url = data.get('url')
        
        if not youtube_url:
            return jsonify({'error': 'YouTube URL is required'}), 400
        
        logger.info(f"Processing URL: {youtube_url[:50]}...")  # Log partial URL
        
        # Step 1: Download audio
        audio_path = download_youtube_audio(youtube_url, app.config['UPLOAD_FOLDER'])
        if not audio_path or not os.path.exists(audio_path):
            logger.error("Audio download failed")
            return jsonify({'error': 'Failed to download audio'}), 500
        
        # Step 2: Transcribe
        transcription = transcribe_audio(audio_path)
        if not transcription:
            logger.error("Transcription failed")
            return jsonify({'error': 'Failed to transcribe audio'}), 500
        
        # Clean up audio file
        try:
            os.remove(audio_path)
        except Exception as e:
            logger.warning(f"Could not delete audio file: {str(e)}")
        

        # Step 3: Summarize (truncate for speed)
        summary = summarize_text(truncate_text(transcription))
        if not summary:
            logger.error("Summarization failed")
            return jsonify({'error': 'Failed to generate summary'}), 500
        
        return jsonify({
            'status': 'success',
            'summary': summary,
            'transcription_length': len(transcription)
        })
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

@app.route("/", methods=["GET"])
def health():
    return "Backend is running!", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)  # Production host/port
import os
import json
import logging
from dotenv import load_dotenv

# Try to import deepgram-sdk, handling potential missing dependency for local dev without it
try:
    from deepgram import DeepgramClient
except ImportError:
    DeepgramClient = None
    print("Warning: deepgram-sdk not installed or version incompatible. DeepgramAudioAgent will not function.")

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DeepgramAudioAgent")

class DeepgramAudioAgent:
    def __init__(self):
        self.api_key = os.getenv("DEEPGRAM_API_KEY")
        if not self.api_key:
            logger.warning("DEEPGRAM_API_KEY not found in environment variables. Deepgram integration disabled.")
            self.client = None
        elif DeepgramClient is None:
            logger.error("deepgram-sdk is missing. Please install it: pip install deepgram-sdk")
            self.client = None
        else:
            try:
                self.client = DeepgramClient(api_key=self.api_key)
                logger.info("Deepgram Client initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Deepgram Client: {e}")
                self.client = None

        # Distress keywords trigger immediate confirmation
        self.distress_keywords = {
            "help", "help me", "ouch", "pain", "fallen", "fall", "emergency", 
            "hurt", "injured", "can't get up", "ambulance", "doctor"
        }

    def analyze_audio_buffer(self, audio_buffer: bytes) -> dict:
        """
        Analyzes a raw audio buffer using Deepgram's Nova-2 model.
        Returns a dictionary with distress analysis results.
        """
        if not self.client:
            return {
                "distress_confirmed": False, 
                "error": "Deepgram client not initialized",
                "transcript": ""
            }

        try:
            # Call the API using the correct v3 SDK path and arguments
            # Note: client.listen.v1.media.transcribe_file expects 'request' as bytes and options as kwargs
            response = self.client.listen.v1.media.transcribe_file(
                request=audio_buffer,
                model="nova-2",
                smart_format=True,
                sentiment=True,
                detect_entities=True,
                punctuate=True,
                language="en",
            )
            
            # Extract transcript and sentiment
            # Check if results/channels/alternatives exist
            if not response.results or not response.results.channels or not response.results.channels[0].alternatives:
                 logger.warning("Deepgram response missing results/channels/alternatives")
                 return {"distress_confirmed": False, "transcript": "", "error": "Empty response"}

            transcript = response.results.channels[0].alternatives[0].transcript
            confidence = response.results.channels[0].alternatives[0].confidence
            
            distress_confirmed = False
            detected_keywords = []

            # Check for distress keywords
            transcript_lower = transcript.lower()
            for keyword in self.distress_keywords:
                if keyword in transcript_lower:
                    distress_confirmed = True
                    detected_keywords.append(keyword)
            
            # Check sentiment if available
            sentiment_score = 0
            if response.results.sentiments and response.results.sentiments.average:
                sentiment_score = response.results.sentiments.average.sentiment_score
                # Strong negative sentiment with keywords increases confidence/priority
                if sentiment_score < -0.5 and detected_keywords:
                    logger.info("Strong negative sentiment detected with distress keywords.")
            
            result = {
                "distress_confirmed": distress_confirmed,
                "transcript": transcript,
                "confidence": confidence,
                "detected_keywords": detected_keywords,
                "sentiment_score": sentiment_score
            }
            logger.info(f"Audio Analysis Result: {result}")
            return result

        except Exception as e:
            logger.error(f"Deepgram API Error: {e}")
            return {
                "distress_confirmed": False,
                "error": str(e),
                "transcript": ""
            }

# --- Snippet for app.py Integration ---
"""
# In app.py:

from deepgram_agent import DeepgramAudioAgent

# Initialize Agent
dg_agent = DeepgramAudioAgent()

@app.route('/analyze_audio_distress', methods=['POST'])
def analyze_audio_distress():
    try:
        # Expecting a file upload named 'header' or raw binary? 
        # Usually for simple integration, we take a file from form-data
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        audio_bytes = file.read()
        
        # Analyze
        result = dg_agent.analyze_audio_buffer(audio_bytes)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
"""

if __name__ == "__main__":
    # Simple test if run directly
    print("Testing DeepgramAudioAgent...")
    agent = DeepgramAudioAgent()
    if agent.client:
        print("Client is ready. Please provide a path to a test wav file to invoke analyze_audio_buffer interactively if needed.")
    else:
        print("Client not initialized (check API Key and SDK).")

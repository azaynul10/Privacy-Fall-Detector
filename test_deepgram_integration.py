import os
import sys
from deepgram_agent import DeepgramAudioAgent

def test():
    print("Testing Deepgram Integration...")
    
    # Check env var directly first to be sure
    key = os.getenv("DEEPGRAM_API_KEY")
    if not key:
        print("ERROR: DEEPGRAM_API_KEY not found in environment.")
        return

    agent = DeepgramAudioAgent()
    if not agent.client:
        print("FAIL: Client not initialized.")
        return

    wav_path = "fall_alert.wav"
    if not os.path.exists(wav_path):
        print(f"WARN: {wav_path} not found. Skipping actual audio test.")
        return

    with open(wav_path, "rb") as f:
        audio_data = f.read()

    print(f"Analyzing {wav_path} ({len(audio_data)} bytes)...")
    try:
        result = agent.analyze_audio_buffer(audio_data)
        print("Analysis Result:")
        print(result)
        if result.get('error'):
             print("FAIL: API returned error.")
        else:
             print("SUCCESS: Analysis verified.")
    except Exception as e:
        print(f"CRITICAL FAIL: {e}")

if __name__ == "__main__":
    test()

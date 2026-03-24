from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import threading
import time
import os
from bob_api import BobAI

app = Flask(__name__)
CORS(app)  # Enable CORS for Unreal

# Initialize Bob AI with voice enabled
bob = BobAI(enable_voice=True, enable_wake_word=True)

@app.route('/ask', methods=['POST'])
def ask_question():
    """Ask a question via API"""
    try:
        data = request.get_json()
        question = data.get('question', '')
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        answer, is_confident = bob.qa_engine.answer_question(question)
        
        return jsonify({
            'question': question,
            'answer': answer,
            'confident': is_confident,
            'status': 'success'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/voice/start', methods=['POST'])
def start_voice():
    """Start voice wake word detection"""
    result = bob.start_voice_mode()
    return jsonify({'message': result, 'status': 'success'})

@app.route('/voice/stop', methods=['POST'])
def stop_voice():
    """Stop voice wake word detection"""
    result = bob.stop_voice_mode()
    return jsonify({'message': result, 'status': 'success'})

@app.route('/status', methods=['GET'])
def get_status():
    """Get Bob's status"""
    return jsonify(bob.get_status())

@app.route('/teach', methods=['POST'])
def teach_bob():
    """Teach Bob new information"""
    try:
        data = request.get_json()
        question = data.get('question', '')
        answer = data.get('answer', '')
        
        if not question or not answer:
            return jsonify({'error': 'Question and answer required'}), 400
        
        # Add to knowledge base
        new_doc = {"text": f"Q: {question}\nA: {answer}", "source": "api_taught"}
        bob.qa_engine.add_document(new_doc)
        
        return jsonify({
            'message': 'Successfully learned new information',
            'question': question,
            'answer': answer,
            'status': 'success'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/voice/test', methods=['POST'])
def test_voice():
    """Test voice functionality by simulating wake word"""
    try:
        if not bob.enable_voice:
            return jsonify({'error': 'Voice not enabled'}), 400
        
        # Simulate wake word detection
        bob.voice.speak("Voice test successful! I can hear and speak.")
        
        return jsonify({
            'message': 'Voice test completed',
            'status': 'success',
            'voice_enabled': bob.enable_voice,
            'listening': bob.is_listening if hasattr(bob, 'is_listening') else False
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/voice/simulate', methods=['POST'])
def simulate_conversation():
    """Simulate a conversation for testing"""
    try:
        data = request.get_json()
        question = data.get('question', 'Hello Bob')
        
        # Simulate the full conversation flow
        bob.voice.speak("Yes!")
        answer, is_confident = bob.qa_engine.answer_question(question)
        bob.voice.speak(answer)
        
        return jsonify({
            'simulated_question': question,
            'answer': answer,
            'confident': is_confident,
            
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/audio/latest', methods=['GET'])
def get_latest_audio():
    """Get the latest audio response file"""
    audio_file = os.path.join('response', 'bob_responses.wav')
    if os.path.exists(audio_file):
        return send_file(audio_file, mimetype='audio/wav')
    return jsonify({'error': 'No audio file found'}), 404

if __name__ == '__main__':
    print("Starting Bob AI API Server with Voice Support...")
    print("API Endpoints:")
    print("  POST /ask - Ask a question")
    print("  POST /teach - Teach new information")
    print("  POST /voice/start - Start voice mode")
    print("  POST /voice/stop - Stop voice mode")
    print("  GET /status - Get status")
    print("\nServer running on http://localhost:5000")
    print("Voice wake word detection available!")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
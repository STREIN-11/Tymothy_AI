from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import time
from src.wake_word.detector import WakeWordDetector
from src.qa_engine.engine import QAEngine
from src.data_loader.loader import DataLoader
from config.config import DATA_DIR, VECTOR_DB_PATH
import os

app = Flask(__name__)
CORS(app)

# Global variables
qa_engine = None
detector = None
listening = False
last_question = ""
last_answer = ""

def initialize_bob():
    
    global qa_engine, detector
    print("Initializing Bob API...")
    
    loader = DataLoader(DATA_DIR)
    qa_engine = QAEngine()
    
    if not os.path.exists(VECTOR_DB_PATH):
        documents = loader.load_all_data()
        qa_engine.documents = documents
        qa_engine.build_index(documents)
    else:
        documents = loader.load_all_data()
        qa_engine.documents = documents
        qa_engine.load_index()
    
    detector = WakeWordDetector()
    detector.start_listening()
    print("Bob API ready!")

def listen_loop():
    global listening, last_question, last_answer
    while True:
        if listening and detector.detect_wake_word():
            question = detector.listen_for_question()
            if question:
                last_question = question
                last_answer = qa_engine.answer_question(question)
                listening = False
        time.sleep(0.1)

@app.route('/start_listening', methods=['POST'])
def start_listening():
    global listening
    listening = True
    return jsonify({"status": "listening", "message": "Bob is now listening for wake word"})

@app.route('/stop_listening', methods=['POST'])
def stop_listening():
    global listening
    listening = False
    return jsonify({"status": "stopped", "message": "Bob stopped listening"})

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.json
    question = data.get('question', '')
    if question:
        answer = qa_engine.answer_question(question)
        return jsonify({"question": question, "answer": answer})
    return jsonify({"error": "No question provided"})

@app.route('/status', methods=['GET'])
def get_status():
    global last_question, last_answer, listening
    return jsonify({
        "listening": listening,
        "last_question": last_question,
        "last_answer": last_answer
    })

if __name__ == '__main__':
    initialize_bob()
    
    # Start listening thread
    listen_thread = threading.Thread(target=listen_loop, daemon=True)
    listen_thread.start()
    
    # Start Flask API
    
    app.run(host='0.0.0.0', port=5000, debug=False)
import os
import time
import threading
import queue
try:
    from src.splash_screen import show_splash, update_splash, close_splash
    SPLASH_AVAILABLE = True
except Exception as e:
    print(f"Splash screen not available: {e}")
    SPLASH_AVAILABLE = False
    def show_splash(): pass
    def update_splash(progress, status): print(f"[{progress}%] {status}")
    def close_splash(): pass

# Global variables for threaded loading
detector = None
qa_engine = None
voice = None
adaptive_learning = None
models_loaded = False
loading_error = None
progress_queue = queue.Queue()

def start_api_server():
    """Start the API server in the same process"""
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    
    app = Flask(__name__)
    CORS(app)
    
    @app.route('/ask', methods=['POST'])
    def ask_question():
        try:
            data = request.get_json()
            question = data.get('question', '')
            
            if not question:
                return jsonify({'error': 'No question provided'}), 400
            
            answer, is_confident = qa_engine.answer_question(question)
            
            # Generate TTS synchronously so audio is ready before we return
            voice.start_new_conversation()
            voice.current_conversation.append(answer)
            voice._save_conversation()  # blocking, not threaded
            
            return jsonify({'answer': answer, 'confident': is_confident})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/audio', methods=['GET'])
    def get_audio():
        """Serve the latest response MP3 file"""
        from flask import send_file
        mp3_path = os.path.join('response', 'bob_responses.mp3')
        if os.path.exists(mp3_path):
            return send_file(os.path.abspath(mp3_path), mimetype='audio/mpeg')
        return jsonify({'error': 'No audio available'}), 404

    @app.route('/status', methods=['GET'])
    def get_status():
        return jsonify({
            'status': 'running',
            'models_loaded': models_loaded,
            'voice_enabled': True
        })
    
    @app.route('/teach', methods=['POST'])
    def teach_bob():
        try:
            data = request.get_json()
            question = data.get('question', '')
            answer = data.get('answer', '')
            
            if not question or not answer:
                return jsonify({'error': 'Question and answer required'}), 400
            
            new_doc = {"text": f"Q: {question}\nA: {answer}", "source": "api_taught"}
            qa_engine.add_document(new_doc)
            
            return jsonify({
                'message': 'Successfully learned new information',
                'question': question,
                'answer': answer,
                'status': 'success'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    print("Starting API server on http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

def load_models_thread():
    """Load heavy models in background thread"""
    
    global detector, qa_engine, voice, adaptive_learning, models_loaded, loading_error
    
    try:
        progress_queue.put((10, "Personalizing your experience..."))
        from src.wake_word.detector import WakeWordDetector
        from src.qa_engine.engine import QAEngine
        from src.data_loader.loader import DataLoader
        from src.voice_output.tts import VoiceOutput
        from src.learning.adaptive_learning import AdaptiveLearning
        from config.config import DATA_DIR, VECTOR_DB_PATH
        
        progress_queue.put((20, "Loading essentials..."))
        adaptive_learning = AdaptiveLearning()
        
        progress_queue.put((30, "Preparing smart responses..."))
        loader = DataLoader(DATA_DIR)
        
        progress_queue.put((40, "Getting voice-ready..."))
        qa_engine = QAEngine()
        
        progress_queue.put((50, "Setting up voice..."))
        voice = VoiceOutput(debug=True)
        
        # Load knowledge base
        if not os.path.exists(VECTOR_DB_PATH):
            progress_queue.put((60, "Organizing knowledge..."))
            documents = loader.load_all_data()
            learned_docs = adaptive_learning.get_learning_documents()
            documents.extend(learned_docs)
            
            if not documents:
                loading_error = "No data files found in 'data' directory. Please add CSV, TXT, or JSON files."
                return
            qa_engine.documents = documents
            progress_queue.put((70, "Indexing information..."))
            qa_engine.build_index(documents)
        else:
            progress_queue.put((60, "Organizing knowledge..."))
            documents = loader.load_all_data()
            learned_docs = adaptive_learning.get_learning_documents()
            documents.extend(learned_docs)
            qa_engine.documents = documents
            
            if documents:
                progress_queue.put((70, "Updating knowledge..."))
                qa_engine.rebuild_index()
            else:
                progress_queue.put((70, "Indexing information..."))
                qa_engine.load_index()
        
        # Load speech recognition (heaviest part)
        progress_queue.put((80, "Loading speech recognition (this takes time)..."))
        detector = WakeWordDetector()
        
        progress_queue.put((95, "Final checks..."))
        detector.start_listening()
        
        progress_queue.put((100, "Ready! Bob AI is starting..."))
        models_loaded = True
        
    except Exception as e:
        loading_error = str(e)
        print(f"Error loading models: {e}")


def main():
    # Show splash screen IMMEDIATELY
    if SPLASH_AVAILABLE:
        show_splash()
    update_splash(5, "Starting Tymor AI Assistant...")
    
    # Start loading models in background thread
    loading_thread = threading.Thread(target=load_models_thread, daemon=True)
    loading_thread.start()
    
    # Process progress updates from background thread
    while not models_loaded and not loading_error:
        try:
            # Check for progress updates from background thread
            progress, status = progress_queue.get_nowait()
            update_splash(progress, status)
        
        except:
            pass
        time.sleep(0.1)
    
    if loading_error:
        update_splash(100, f"Error: {loading_error}")
        time.sleep(3)
        close_splash()
        print(loading_error)
        return
    
    # Process any remaining progress updates
    while not progress_queue.empty():
        try:
            progress, status = progress_queue.get_nowait()
            update_splash(progress, status)
        except:
            break
    
    time.sleep(1)
    close_splash()
    
    # Start API server in background thread
    api_thread = threading.Thread(target=start_api_server, daemon=True)
    api_thread.start()
    time.sleep(2)  # Give API server time to start
    
    print("=" * 60)
    print("Tymor AI ready. API Server running on http://localhost:5000")
    print("Wake word listening DISABLED — use the web frontend.")
    print("=" * 60)
    print("Press Ctrl+C to exit.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down Tymor AI...")

if __name__ == "__main__":
    main()

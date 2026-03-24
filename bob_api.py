import os
import threading
import time
from src.wake_word.detector import WakeWordDetector
from src.qa_engine.engine import QAEngine
from src.data_loader.loader import DataLoader
from src.voice_output.tts import VoiceOutput
from config.config import DATA_DIR, VECTOR_DB_PATH

class BobAI:
    def __init__(self, enable_voice=True, enable_wake_word=True):
        """
        Initialize Bob AI for Unreal integration
        
        Args:
            enable_voice: Enable text-to-speech output
            enable_wake_word: Enable wake word detection
        """
        self.enable_voice = enable_voice
        self.enable_wake_word = enable_wake_word
        self.is_initialized = False
        self.is_listening = False
        
        # Initialize components
        self._init_components()
        
    def _init_components(self):
        """Initialize AI components"""
        print("Initializing Bob AI...")
        
        # Load QA engine
        loader = DataLoader(DATA_DIR)
        self.qa_engine = QAEngine()
        
        if self.enable_voice:
            self.voice = VoiceOutput(debug=False)
        
        # Load or build knowledge base
        if not os.path.exists(VECTOR_DB_PATH):
            print("Building knowledge base...")
            documents = loader.load_all_data()
            if documents:
                self.qa_engine.documents = documents
                self.qa_engine.build_index(documents)
                print(f"Indexed {len(documents)} documents.")
            else:
                print("No data files found.")
        else:
            documents = loader.load_all_data()
            self.qa_engine.documents = documents
            self.qa_engine.load_index()
        
        # Initialize wake word detector if enabled
        if self.enable_wake_word:
            self.detector = WakeWordDetector()
            
        self.is_initialized = True
        print("Bob AI ready!")
    
    def ask_question(self, question_text):
        """
        Ask a question and get answer (for direct text input)
        
        Args:
            question_text (str): The question to ask
            
        Returns:
            str: The answer
        """
        if not self.is_initialized:
            return "AI not initialized"
        
        answer = self.qa_engine.answer_question(question_text)
        
        if self.enable_voice:
            self.voice.speak(answer)
            
        return answer
    
    def start_voice_mode(self):
        """Start voice interaction mode with wake word detection"""
        if not self.enable_wake_word:
            return "Wake word detection disabled"
        
        if self.is_listening:
            return "Already listening"
        
        self.detector.start_listening()
        self.is_listening = True
        
        # Start background thread for voice interaction
        self.voice_thread = threading.Thread(target=self._voice_loop, daemon=True)
        self.voice_thread.start()
        
        return "Voice mode started"
    
    def stop_voice_mode(self):
        """Stop voice interaction mode"""
        if not self.is_listening:
            return "Not listening"
        
        self.is_listening = False
        if hasattr(self, 'detector'):
            self.detector.stop()
        
        return "Voice mode stopped"
    
    def _voice_loop(self):
        """Background voice interaction loop"""
        while self.is_listening:
            try:
                if self.detector.detect_wake_word():
                    if self.enable_voice:
                        self.voice.speak("Yes!")
                    
                    question = self.detector.listen_for_question()
                    
                    if question:
                        answer = self.qa_engine.answer_question(question)
                        if self.enable_voice:
                            self.voice.speak(answer)
                        
                        # You can add callback here for Unreal
                        self._on_question_answered(question, answer)
                    
                time.sleep(0.1)
            
            except:
                pass
    
    def _on_question_answered(self, question, answer):
        """Callback when question is answered (override in Unreal)"""
        print(f"Q: {question}")
        print(f"A: {answer}")
    
    def get_status(self):
        """Get current status"""
        return {
            "initialized": self.is_initialized,
            "listening": self.is_listening,
            "voice_enabled": self.enable_voice,
            "wake_word_enabled": self.enable_wake_word
        }

# Simple usage example
if __name__ == "__main__":
    # For Unreal, you'd import this class and use it
    bob = BobAI(enable_voice=True, enable_wake_word=True)
    
    # Direct question (for UI input)
    answer = bob.ask_question("What is your name?")
    print(f"Answer: {answer}")
    
    # Start voice mode (for voice interaction)
    bob.start_voice_mode()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        bob.stop_voice_mode()
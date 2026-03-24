import speech_recognition as sr
import threading

class ContinuousDetector:
    def __init__(self, wake_words):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
        self.microphone = sr.Microphone()
        self.wake_words = wake_words
        self.listening = False
        
        print("Calibrating microphone...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Microphone ready!")
    
    def start_listening(self):
        """Start continuous background listening"""
        self.stop_listening = self.recognizer.listen_in_background(
            self.microphone, 
            self._audio_callback,
            phrase_time_limit=3
        )
        print("Listening for wake word...")
    
    def _audio_callback(self, recognizer, audio):
        """Background callback for audio processing"""
        if self.listening:
            return
        
        try:
            text = recognizer.recognize_sphinx(audio).lower()
            if text and any(word in text for word in self.wake_words):
                print(f"Wake word detected: {text}")
                self.listening = True
        
        except:
            pass
    
    def detect_wake_word(self):
        """Check if wake word was detected"""
        if self.listening:
            self.listening = False
            return True
        return False
    
    def listen_for_question(self):
        """Listen for a question after wake word"""
        try:
            with self.microphone as source:
                print("Listening for your question...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            print("Processing...")
            text = self.recognizer.recognize_sphinx(audio)
            return text.strip()
        except sr.WaitTimeoutError:
            return ""
        except Exception as e:
            print(f"Error: {e}")
            return ""
    
    def stop(self):
        if hasattr(self, 'stop_listening'):
            self.stop_listening(wait_for_stop=False)

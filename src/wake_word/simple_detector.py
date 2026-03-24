import speech_recognition as sr
import threading
import time

class SimpleDetector:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
        self.microphone = sr.Microphone()
        
        # Adjust for ambient noise
        print("Calibrating microphone...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Ready!")
    
    def listen_for_speech(self):
        """Listen and return recognized text"""
        try:
            with self.microphone as source:
                print("Listening...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
            print("Processing...")
            # Try offline recognition first (Sphinx)
            try:
                text = self.recognizer.recognize_sphinx(audio)
                return text.lower()
            except:
                # Fallback to Vosk if available
                try:
                    text = self.recognizer.recognize_vosk(audio)
                    return text.lower()
                except:
                    return ""
        except sr.WaitTimeoutError:
            return ""
        except Exception as e:
            print(f"Error: {e}")
            return ""
    
    def detect_wake_word(self, wake_words):
        """Check if wake word is in text"""
        text = self.listen_for_speech()
        if text:
            print(f"Heard: {text}")
            return any(word in text for word in wake_words)
        return False
    
    def listen_for_question(self):
        """Listen for a question"""
        return self.listen_for_speech()
    
    def stop(self):
        pass

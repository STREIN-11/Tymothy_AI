import sounddevice as sd
import numpy as np
import queue
import threading
import time
from pynput import keyboard

class HybridDetector:
    def __init__(self):
        self.sample_rate = 16000
        self.audio_queue = queue.Queue(maxsize=50)
        self.wake_detected = False
        self.space_pressed = False
        
    def audio_callback(self, indata, frames, time_info, status):
        """Callback for audio stream"""
        self.audio_queue.put(indata.copy())
    
    def on_press(self, key):
        """Keyboard listener"""
        try:
            if key == keyboard.Key.space:
                self.space_pressed = True
                print("\n[SPACE pressed - Listening...]")
        
        
        except:
            pass
    
    def start_listening(self):
        """Start audio stream and keyboard listener"""
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype='float32',
            blocksize=2048,
            callback=self.audio_callback
        )
        self.stream.start()
        
        # Start keyboard listener
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press)
        self.keyboard_listener.start()
        
        print("\n" + "="*60)
        print("tom is ready!")
        print("="*60)
        print("\nWAKE OPTIONS:")
        print("  1. Press SPACEBAR to activate")
        print("  2. Clap 2 times quickly")
        print("  3. Make a loud sound")
        print("\nPress Ctrl+C to exit\n")
        
        # Start detection thread
        self.running = True
        self.detect_thread = threading.Thread(target=self._detect_loop, daemon=True)
        self.detect_thread.start()
    
    def _detect_loop(self):
        """Background thread for wake word detection"""
        loud_sounds = []
        
        while self.running:
            try:
                audio = self.audio_queue.get(timeout=0.1)
                energy = np.sqrt(np.mean(audio**2))
                
                # Detect loud sound
                if energy > 0.15:
                    current_time = time.time()
                    loud_sounds.append(current_time)
                    loud_sounds = [t for t in loud_sounds if current_time - t < 1.5]
                    
                    # 2 loud sounds within 1.5 seconds
                    if len(loud_sounds) >= 2:
                        time_diff = loud_sounds[-1] - loud_sounds[-2]
                        if 0.2 < time_diff < 1.2:
                            print("\n[Wake detected - Listening...]")
                            self.wake_detected = True
                            loud_sounds.clear()
                            time.sleep(0.3)
                            
            except queue.Empty:
                pass
            
            except:
                pass
    
    def detect_wake_word(self):
        """Check if wake word detected"""
        if self.wake_detected or self.space_pressed:
            self.wake_detected = False
            self.space_pressed = False
            return True
        return False
    
    def listen_for_question(self):
        """Record question"""
        # Clear queue
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except:
                break
        
        print("Speak your question now...")
        print("(Stay silent for 1.5 seconds when done)")
        
        audio_chunks = []
        silence_chunks = 0
        max_silence = 22  # ~1.5 seconds
        recording = False
        
        start_time = time.time()
        
        while silence_chunks < max_silence and (time.time() - start_time) < 8:
            try:
                audio = self.audio_queue.get(timeout=0.1)
                energy = np.sqrt(np.mean(audio**2))
                
                if energy > 0.02:
                    audio_chunks.append(audio)
                    silence_chunks = 0
                    recording = True
                    print("●", end="", flush=True)
                elif recording:
                    audio_chunks.append(audio)
                    silence_chunks += 1
                    
            except:
                if recording:
                    silence_chunks += 1
        
        print("\n")
        
        if not audio_chunks:
            return ""
        
        # Check if user spoke
        total_audio = np.concatenate(audio_chunks)
        avg_energy = np.sqrt(np.mean(total_audio**2))
        
        if avg_energy > 0.03:
            # Prompt for text input since we don't have STT
            print("Type your question (or press Enter to skip):")
            question = input(">>> ").strip()
            return question
        
        return ""
    
    def stop(self):
        """Stop listening"""
        self.running = False
        if hasattr(self, 'keyboard_listener'):
            self.keyboard_listener.stop()
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()

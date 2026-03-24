import sounddevice as sd
import numpy as np
import queue
import threading
import time

class CustomDetector:
    def __init__(self):
        self.sample_rate = 16000
        self.audio_queue = queue.Queue(maxsize=50)
        self.is_listening = False
        self.wake_detected = False
        self.question_audio = []
        
    def audio_callback(self, indata, frames, time_info, status):
        """Callback for audio stream"""
        if status:
            print(f"Audio: {status}")
        self.audio_queue.put(indata.copy())
    
    def start_listening(self):
        """Start audio stream"""
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype='float32',
            blocksize=2048,
            callback=self.audio_callback
        )
        self.stream.start()
        print("Microphone active - clap 2 times or press SPACE then speak")
        
        # Start detection thread
        self.running = True
        self.detect_thread = threading.Thread(target=self._detect_loop, daemon=True)
        self.detect_thread.start()
    
    def _detect_loop(self):
        """Background thread for wake word detection"""
        clap_times = []
        
        while self.running:
            try:
                audio = self.audio_queue.get(timeout=0.1)
                
                # Calculate audio energy
                energy = np.sqrt(np.mean(audio**2))
                
                # Detect loud sound (clap or "Bob")
                if energy > 0.1:  # Threshold for loud sound
                    current_time = time.time()
                    clap_times.append(current_time)
                    
                    # Keep only recent claps (last 2 seconds)
                    clap_times = [t for t in clap_times if current_time - t < 2.0]
                    
                    # Check for 2 claps within 1 second
                    if len(clap_times) >= 2:
                        time_diff = clap_times[-1] - clap_times[-2]
                        if 0.2 < time_diff < 1.0:
                            print("Wake signal detected!")
                            self.wake_detected = True
                            clap_times.clear()
                            time.sleep(0.5)  # Debounce
                            
            except queue.Empty:
                pass
            except Exception as e:
                print(f"Detection error: {e}")
    
    def detect_wake_word(self):
        """Check if wake word detected"""
        if self.wake_detected:
            self.wake_detected = False
            return True
        return False
    
    def listen_for_question(self):
        """Record question after wake word"""
        # Clear queue
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except:
                break
        
        print("Listening for your question...")
        print("(Speak now, then stay silent for 2 seconds)")
        
        audio_chunks = []
        silence_chunks = 0
        max_silence = 30  # ~2 seconds of silence
        recording = False
        
        start_time = time.time()
        max_duration = 10  # Maximum 10 seconds
        
        while silence_chunks < max_silence and (time.time() - start_time) < max_duration:
            try:
                audio = self.audio_queue.get(timeout=0.1)
                energy = np.sqrt(np.mean(audio**2))
                
                # Detect speech
                if energy > 0.02:  # Lower threshold for speech
                    audio_chunks.append(audio)
                    silence_chunks = 0
                    recording = True
                    print(".", end="", flush=True)
                elif recording:
                    audio_chunks.append(audio)
                    silence_chunks += 1
                    
            except queue.Empty:
                if recording:
                    silence_chunks += 1
        
        print()
        
        if not audio_chunks:
            return ""
        
        # Convert to text using simple keyword matching
        # Since we don't have speech-to-text, return a placeholder
        print("Processing audio...")
        
        # Calculate total energy to determine if user spoke
        total_audio = np.concatenate(audio_chunks)
        avg_energy = np.sqrt(np.mean(total_audio**2))
        
        if avg_energy > 0.03:
            # User spoke something
            return "[SPEECH_DETECTED]"
        else:
            return ""
    
    def stop(self):
        """Stop listening"""
        self.running = False
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()

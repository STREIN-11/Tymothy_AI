import sounddevice as sd
import numpy as np
import whisper
import queue
import time
import struct
import os
import sys

class WakeWordDetector:
    def __init__(self):
        print("Loading Whisper model...")
        
        # Fix Whisper asset path for PyInstaller
        if getattr(sys, 'frozen', False):
            # Running in PyInstaller bundle
            whisper_module = whisper
            whisper_path = os.path.dirname(whisper_module.__file__)
            assets_path = os.path.join(whisper_path, 'assets')
            if not os.path.exists(assets_path):
                # Create assets directory and copy from temp
                os.makedirs(assets_path, exist_ok=True)
                print(f"Created Whisper assets directory: {assets_path}")
        
        self.model = whisper.load_model("tiny")
        self.sample_rate = 16000
        self.audio_queue = queue.Queue(maxsize=100)
        self.stream = None
        print("Ready!")
        
    def audio_callback(self, indata, frames, time_info, status):
        """Callback for audio stream"""
        if not self.audio_queue.full():
            self.audio_queue.put(indata.copy())
    
    def _normalize_audio(self, audio_data):
        """Normalize audio with gain boost"""
        audio_data = np.nan_to_num(audio_data, nan=0.0, posinf=0.0, neginf=0.0)
        
        # Apply gain boost (amplify by 3x)
        audio_data = audio_data * 3.0
        
        # Clip to prevent distortion
        audio_data = np.clip(audio_data, -1.0, 1.0)
        
        # Normalize
        max_val = np.abs(audio_data).max()
        if max_val > 0:
            audio_data = audio_data / max_val
        return audio_data.astype(np.float32)
        
    def start_listening(self):
        """Start audio stream"""
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            blocksize=4096,
            dtype='float32',
            channels=1,
            callback=self.audio_callback
        )
        self.stream.start()
        print("\n" + "="*60)
        print("READY! Press SPACEBAR then speak, or say 'tom' loudly")
        print("="*60 + "\n")
        
    def detect_wake_word(self):
        """Simplified wake word detection - any loud sound triggers"""
        try:
            # Collect audio chunks
            chunks = []
            for _ in range(8):  # Collect more audio
                try:
                    data = self.audio_queue.get(timeout=0.1)
                    chunks.append(data)
                
                except:
                    pass
            
            if not chunks:
                return False
            
            audio = np.concatenate(chunks).flatten()
            energy = np.sqrt(np.mean(audio**2))
            
            # Much lower threshold - trigger on any speech
            if energy > 0.005:  # Very low threshold
                print(f"Audio detected (energy: {energy:.4f})")
                
                # Collect more audio for transcription
                for _ in range(15):
                    try:
                        chunks.append(self.audio_queue.get(timeout=0.05))
                    
                    except:
                        pass
                
                audio = np.concatenate(chunks).flatten()
                audio = self._normalize_audio(audio)
                
                try:
                    # Use simpler transcription settings
                    result = self.model.transcribe(
                        audio,
                        language="en",
                        fp16=False,
                        temperature=0.0,
                        no_speech_threshold=0.3,  # Lower threshold
                        word_timestamps=False
                    )
                    text = result["text"].lower().strip()
                    print(f"Heard: '{text}'")
                    
                    # Check for wake words
                    wake_words = ["tom", "hey tom", "hi tom", "hello tom"]
                    for wake_word in wake_words:
                        if wake_word in text:
                            print(f"✓ Wake word detected: '{wake_word}'")
                            # Clear queue
                            while not self.audio_queue.empty():
                                try:
                                    self.audio_queue.get_nowait()
                                except:
                                    break
                            return True
                    
                    # If no wake word but speech detected, show what was heard
                    if len(text) > 2:
                        print(f"Not a wake word: '{text}'")
                        
                except Exception as e:
                    print(f"Transcription error: {e}")
                    pass
        except Exception as e:
            print(f"Detection error: {e}")
            pass
        
        return False
    
    
    def listen_for_question(self, allow_cancel=False):
        """Listen for question"""
        # Clear queue
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except:
                break
        
        time.sleep(0.3)
        
        if allow_cancel:
            print("Listening for your answer... (say 'cancel' to skip)")
        else:
            print("Listening for your question...")
            
        audio_chunks = []
        silence_count = 0
        max_silence = 15  # Reduced from 18
        recording = False
        start_time = time.time()
        min_recording_time = 0.5  # Minimum 0.5 seconds of speech
        
        while silence_count < max_silence and (time.time() - start_time) < 10:
            try:
                data = self.audio_queue.get(timeout=0.1)
                energy = np.sqrt(np.mean(data**2))
                
                if energy > 0.01:  # Even lower - from 0.015 to 0.01
                    audio_chunks.append(data)
                    silence_count = 0
                    recording = True
                    print("●", end="", flush=True)
                elif recording:
                    audio_chunks.append(data)
                    silence_count += 1
            except:
                if recording:
                    silence_count += 1
        
        print("\nProcessing...")
        
        # More lenient minimum - just need 5 chunks (~0.5 seconds)
        if len(audio_chunks) < 5:
            return ""
        
        audio_data = np.concatenate(audio_chunks).flatten()
        audio_data = self._normalize_audio(audio_data)
        
        # Check if there's any speech at all
        avg_energy = np.sqrt(np.mean(audio_data**2))
        if avg_energy < 0.01:  # Very low threshold
            return ""
        
        try:
            result = self.model.transcribe(
                audio_data,
                language="en",
                fp16=False,
                temperature=0.0,
                no_speech_threshold=0.5,  # Lower threshold
                compression_ratio_threshold=2.4,
                logprob_threshold=-1.0
            )
            text = result["text"].strip().lower()
            
            # Check for cancel command if allowed
            if allow_cancel and ("cancel" in text or "skip" in text or "never mind" in text):
                return "CANCEL"
            
            # Return even if short
            if len(text) > 0:
                return text
            return ""
        except Exception as e:
            print(f"Error: {e}")
            return ""
    
    def stop(self):
        """Stop listening"""
        if self.stream:
            self.stream.stop()
            self.stream.close()

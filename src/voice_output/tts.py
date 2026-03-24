import pyttsx3
import threading
import os
import time
import subprocess
import sys

class VoiceOutput:
    def __init__(self, debug=True):
        self.debug = debug
        self.response_file = os.path.join("response", "bob_responses.wav")
        self.current_conversation = []
        
        # Try to find the best TTS option available
        self.tts_method = self._detect_best_tts()
        
    def _detect_best_tts(self):
        """Detect the best available TTS method"""
        
        # Option 1: Try Edge TTS (high quality, human-like)
        try:
            import edge_tts
            if self.debug:
                print("Edge TTS detected")
            return 'edge'
        except ImportError:
            pass
        
        # Option 2: Try Windows SAPI (built-in, high quality)
        if os.name == 'nt':
            try:
                import win32com.client
                if self.debug:
                    print("Windows SAPI detected")
                return 'sapi'
            except ImportError:
                pass
        
        # Option 3: Fallback to pyttsx3
        return 'pyttsx3'
    
    def speak(self, text: str):
        if self.debug:
            print(f"Bob: {text}")
        
        if self.tts_method == 'edge':
            self._speak_edge(text)
        elif self.tts_method == 'sapi':
            self._speak_sapi(text)
        else:
            self._speak_pyttsx3(text)
        
        # Add to current conversation
        self.current_conversation.append(text)
    
    def _speak_edge(self, text: str):
        """Use Edge TTS with Eric Neural voice"""
        try:
            import edge_tts
            import asyncio
            import tempfile
            import os
            import sounddevice as sd
            import soundfile as sf
            
            async def generate_speech():
                try:
                    communicate = edge_tts.Communicate(text, "en-US-EricNeural")
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                        await communicate.save(tmp_file.name)
                        # Verify file was created and has content
                        if os.path.exists(tmp_file.name) and os.path.getsize(tmp_file.name) > 0:
                            return tmp_file.name
                        else:
                            
                            raise Exception("No audio data generated")
                except Exception as e:
                    raise Exception(f"Edge TTS communication failed: {e}")
            
            # Generate speech with timeout
            try:
                audio_file = asyncio.run(asyncio.wait_for(generate_speech(), timeout=10.0))
            except asyncio.TimeoutError:
                
                raise Exception("Edge TTS timeout")
            
            # Play audio
            data, samplerate = sf.read(audio_file)
            sd.play(data, samplerate)
            sd.wait()
            
            # Clean up
            os.unlink(audio_file)
            
            if self.debug:
                print(f"Generated Edge TTS Eric Neural audio for: {text[:50]}...")
                
        except Exception as e:
            if self.debug:
                print(f"Edge TTS Error: {e}, falling back to SAPI")
            self._speak_sapi(text)
    
    def _speak_sapi(self, text: str):
        """Use Windows SAPI for high-quality voice"""
        try:
            import win32com.client
            
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            voices = speaker.GetVoices()
            
            # Look for best male voice
            male_voice = None
            for i in range(voices.Count):
                voice = voices.Item(i)
                voice_name = voice.GetDescription().lower()
                
                # Prefer Mark, David, or any male voice
                if any(name in voice_name for name in ['mark', 'david', 'male']):
                    male_voice = voice
                    break
            
            if male_voice:
                speaker.Voice = male_voice
                if self.debug:
                    print(f"Using SAPI voice: {male_voice.GetDescription()}")
            
            # Set speech rate (0-10, 5 is normal)
            speaker.Rate = 2  # Slightly slower for clarity
            
            speaker.Speak(text)
            
        except Exception as e:
            if self.debug:
                print(f"SAPI Error: {e}, falling back to pyttsx3")
            self._speak_pyttsx3(text)
    
    def _speak_pyttsx3(self, text: str):
        """Fallback to pyttsx3 with best male voice"""
        try:
            engine = pyttsx3.init()
            
            # Get available voices
            voices = engine.getProperty('voices')
            
            # Look for male voices
            male_voice = None
            for voice in voices:
                voice_name = voice.name.lower()
                if any(name in voice_name for name in ['david', 'mark', 'male', 'man']):
                    male_voice = voice
                    break
            
            if male_voice:
                engine.setProperty('voice', male_voice.id)
                if self.debug:
                    print(f"Using pyttsx3 voice: {male_voice.name}")
            
            # Set speech properties
            engine.setProperty('rate', 150)    # Speed
            engine.setProperty('volume', 0.9)  # Volume
            
            engine.say(text)
            engine.runAndWait()
            engine.stop()
            
        except Exception as e:
            if self.debug:
                print(f"pyttsx3 Error: {e}")
    
    def start_new_conversation(self):
        """Clear conversation for new interaction"""
        self.current_conversation = []
    
    def save_current_conversation(self):
        """Save complete conversation to file (replace previous)"""
        if not self.current_conversation:
            return
            
        threading.Thread(target=self._save_conversation, daemon=True).start()
    
    def _save_conversation(self):
        """Save complete conversation to file"""
        try:
            if not self.current_conversation:
                return
            
            # Ensure response directory exists
            response_dir = os.path.dirname(self.response_file)
            if not os.path.exists(response_dir):
                os.makedirs(response_dir, exist_ok=True)
            
            # Create combined text for TTS
            full_conversation = " ".join(self.current_conversation)
            
            if self.tts_method == 'edge':
                self._save_edge(full_conversation)
            elif self.tts_method == 'sapi':
                self._save_sapi(full_conversation)
            else:
                self._save_pyttsx3(full_conversation)
                
        except Exception as e:
            if self.debug:
                print(f"Audio save error: {e}")
    
    def _save_edge(self, text: str):
        """Save using Edge TTS — MP3 only, no WAV conversion needed"""
        try:
            import edge_tts
            import asyncio

            async def save_speech():
                mp3_file = os.path.join(os.path.dirname(self.response_file), 'bob_responses.mp3')
                communicate = edge_tts.Communicate(text, "en-US-EricNeural")
                await communicate.save(mp3_file)
                if not os.path.exists(mp3_file) or os.path.getsize(mp3_file) == 0:
                    raise Exception("No audio data saved")
                if self.debug:
                    print(f"Edge TTS saved: {mp3_file}")

            asyncio.run(asyncio.wait_for(save_speech(), timeout=15.0))
        except Exception as e:
            if self.debug:
                print(f"Edge TTS save error: {e}")
            self._save_sapi(text)
    
    def _save_sapi(self, text: str):
        """Save using SAPI"""
        try:
            import win32com.client
            
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            file_stream = win32com.client.Dispatch("SAPI.SpFileStream")
            
            # Use same voice and rate as speaking
            voices = speaker.GetVoices()
            for i in range(voices.Count):
                voice = voices.Item(i)
                voice_name = voice.GetDescription().lower()
                if any(male_name in voice_name for male_name in ['david', 'mark', 'male']):
                    speaker.Voice = voice
                    break
            
            speaker.Rate = 2
            
            file_stream.Open(self.response_file, 3)  # 3 = write mode
            speaker.AudioOutputStream = file_stream
            speaker.Speak(text)
            file_stream.Close()
            
        except Exception as e:
            if self.debug:
                print(f"SAPI save error: {e}")
    
    def _save_pyttsx3(self, text: str):
        """Save using pyttsx3"""
        try:
            engine = pyttsx3.init()
            
            voices = engine.getProperty('voices')
            male_voice = None
            
            for voice in voices:
                voice_name = voice.name.lower()
                if any(name in voice_name for name in ['david', 'mark', 'male', 'man']):
                    male_voice = voice
                    break
            
            if male_voice:
                engine.setProperty('voice', male_voice.id)
            
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 0.9)
            
            engine.save_to_file(text, self.response_file)
            engine.runAndWait()
            engine.stop()
            
        except Exception as e:
            if self.debug:
                print(f"pyttsx3 save error: {e}")
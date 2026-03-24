from bob_api import BobAI
import time

class UnrealBobIntegration:
    def __init__(self):
        # Initialize Bob AI (no server needed!)
        self.bob = BobAI(
            enable_voice=True,      # Enable TTS
            enable_wake_word=True   # Enable wake word detection
        )
        
        # Override callback for Unreal events
        self.bob._on_question_answered = self.on_ai_response
        
    def on_ai_response(self, question, answer):
        """Called when AI answers a question - send to Unreal"""
        # This is where you'd send data to Unreal Engine
        print(f"[UNREAL EVENT] Question: {question}")
        print(f"[UNREAL EVENT] Answer: {answer}")
        
        # Example: Trigger Unreal Blueprint event
        # unreal.trigger_blueprint_event("OnAIResponse", question, answer)
        
    def start_ai_voice(self):
        """Start voice interaction"""
        result = self.bob.start_voice_mode()
        print(f"Voice mode: {result}")
        
    def stop_ai_voice(self):
        """Stop voice interaction"""
        result = self.bob.stop_voice_mode()
        print(f"Voice mode: {result}")
        
    def ask_direct_question(self, question):
        """Ask question directly (from UI input)"""
        answer = self.bob.ask_question(question)
        return answer
        
    def get_ai_status(self):
        """Get AI status for Unreal UI"""
        return self.bob.get_status()

# Usage in Unreal:
if __name__ == "__main__":
    # Initialize AI integration
    unreal_ai = UnrealBobIntegration()
    
    # Example 1: Direct question (from Unreal UI)
    answer = unreal_ai.ask_direct_question("What is your name?")
    print(f"Direct answer: {answer}")
    
    # Example 2: Start voice mode (for voice interaction)
    unreal_ai.start_ai_voice()
    
    print("Say 'Bob' to interact...")
    
    try:
        # Keep running (in Unreal, this would be handled by game loop)
        while True:
            time.sleep(1)
            
            # Check status
            status = unreal_ai.get_ai_status()
            if not status["listening"]:
                break
                
    except KeyboardInterrupt:
        unreal_ai.stop_ai_voice()
        print("AI stopped")

"""
UNREAL INTEGRATION STEPS:

1. Copy entire Offline_Ai folder to your Unreal project
2. Install Python packages in Unreal's Python environment
3. Import BobAI class in your Unreal Python scripts
4. Use the methods above in Blueprint/C++ callbacks

UNREAL BLUEPRINT EVENTS:
- OnAIResponse(question: string, answer: string)
- OnWakeWordDetected()
- OnListeningStarted()
- OnListeningStopped()

NO SERVER NEEDED - Direct library integration!
"""
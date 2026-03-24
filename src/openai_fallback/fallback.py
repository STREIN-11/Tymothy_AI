import os
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import pytz

load_dotenv()

class OpenAIFallback:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=api_key) if api_key else None
        self.enabled = self.client is not None
        print(f"[OpenAI Fallback] Enabled: {self.enabled}")
    
    def get_answer(self, question: str, context: str = "") -> str:
        """Get answer from OpenAI when local model fails"""
        if not self.enabled:
            print("[OpenAI Fallback] Not enabled - no API key")
            return None
        
        try:
            print(f"[OpenAI Fallback] Calling API for: {question}")
            
            now = datetime.now(pytz.timezone(os.getenv('TIMEZONE', 'Asia/Kolkata')))
            current_time = now.strftime("%I:%M %p")
            current_date = now.strftime("%B %d, %Y")
            
            if context:
                system_prompt = f"You are Bob, a helpful AI assistant. Current time: {current_time}, Date: {current_date}. Use the provided context to answer. Provide specific details and names when available."
            else:
                system_prompt = f"You are Bob, a knowledgeable AI assistant. Current time: {current_time}, Date: {current_date}. Answer with specific information from your knowledge. Provide names, dates, and details. Never say you don't have information - use what you know."
            
            messages = [{"role": "system", "content": system_prompt}]
            
            if context:
                messages.append({"role": "system", "content": context})
            
            messages.append({"role": "user", "content": question})
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=200,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content.strip()
            print(f"[OpenAI Fallback] Got answer: {answer[:50]}...")
            return answer
        except Exception as e:
            print(f"[OpenAI API error] {e}")
            return None

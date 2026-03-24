import json
import os
from datetime import datetime
from typing import Dict, List
from config.config import DATA_DIR

class AdaptiveLearning:
    def __init__(self, learning_file: str = "learned_conversations.json", max_conversations: int = 1000):
        
        self.learning_file = os.path.join(DATA_DIR, learning_file)
        self.max_conversations = max_conversations
        self.conversations = self.load_conversations()
        
    def load_conversations(self) -> List[Dict]:
        if os.path.exists(self.learning_file):
            with open(self.learning_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_conversations(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        # Keep only recent conversations if limit exceeded
        if len(self.conversations) > self.max_conversations:
            self.conversations = self.conversations[-self.max_conversations:]
        
        with open(self.learning_file, 'w', encoding='utf-8') as f:
            json.dump(self.conversations, f, indent=2, ensure_ascii=False)
    
    def add_conversation(self, question: str, answer: str, user_feedback: str = None):
        # Check for duplicate questions to avoid redundancy
        for conv in self.conversations:
            if conv["question"].lower().strip() == question.lower().strip():
                # Update existing conversation with new answer if different
                if conv["answer"] != answer:
                    conv["answer"] = answer
                    conv["timestamp"] = datetime.now().isoformat()
                return
        
        conversation = {
            "question": question,
            "answer": answer,
            "timestamp": datetime.now().isoformat(),
            "feedback": user_feedback
        }
        self.conversations.append(conversation)
        self.save_conversations()
    
    def get_learning_documents(self) -> List[Dict[str, str]]:
        documents = []
        for conv in self.conversations:
            if conv.get("feedback") != "bad":  # Only learn from good/neutral responses
                doc_text = f"Q: {conv['question']}\nA: {conv['answer']}"
                documents.append({
                    "text": doc_text,
                    "source": "learned_conversation",
                    "timestamp": conv["timestamp"]
                })
        return documents
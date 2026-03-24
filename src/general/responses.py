import random
import re

class GeneralResponses:
    def __init__(self):
        self.responses = {
            'greeting': [
                "Hello! I'm Timmy, your AI assistant. How can I help you today?",
                "Hi there! I'm Timmy. What would you like to know?",
                "Hey! Timmy here, ready to assist you."
            ],
            'how_are_you': [
                "I'm doing great, thanks for asking! How are you?",
                "I'm functioning perfectly and ready to help!",
                "I'm excellent! What can I do for you today?"
            ],
            'about_you': [
                "I'm Timmy, an offline AI assistant. I can answer questions based on my knowledge base and learn new things from you.",
                "I'm Timmy! I'm designed to help answer questions and learn from our conversations. I work completely offline for your privacy.",
                "I'm Timmy, your personal AI assistant. I can help with questions and I'm always learning new things!"
            ],
            'thank_you': [
                "You're welcome! Happy to help!",
                "No problem at all!",
                "Glad I could help!"
            ],
            'goodbye': [
                "Goodbye! Feel free to ask me anything anytime.",
                "See you later! I'll be here when you need me.",
                "Take care! Come back anytime you have questions."
            ],
            'what_can_you_do': [
                "I can answer questions from my knowledge base, learn new information from you, and help with various topics. Just ask me anything!",
                "I can help answer questions, learn new things you teach me, and assist with information you need. What would you like to know?",
                "I'm here to answer your questions and learn from you. I work offline and can help with various topics!"
            ]
        }
        
        self.patterns = {
            'greeting': [r'\b(hi|hello|hey)\b', r'\bgood (morning|afternoon|evening)\b'],
            'how_are_you': [r'\bhow are you\b', r'\bhow\'re you\b', r'\bhow do you feel\b'],
            'about_you': [r'\b(who are you|what are you|tell me about yourself|about you)\b'],
            'thank_you': [r'\b(thank you|thanks|thank u)\b'],
            'goodbye': [r'\b(bye|goodbye|see you|farewell)\b'],
            'what_can_you_do': [r'\b(what can you do|what do you do|your capabilities|help me)\b']
        }
    
    def get_response(self, question: str) -> str:
        """Check if question matches general patterns and return appropriate response"""
        question_lower = question.lower().strip()
        
        for category, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, question_lower):
                    return random.choice(self.responses[category])
        
        return None  # No general response found
    
    def is_general_question(self, question: str) -> bool:
        """Check if the question is a general conversational question"""
        return self.get_response(question) is not None
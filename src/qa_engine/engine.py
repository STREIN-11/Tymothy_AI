import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict
from config.config import EMBEDDING_MODEL, EMBEDDING_CACHE, VECTOR_DB_PATH
import os

class QAEngine:
    def __init__(self):
        if os.path.exists(EMBEDDING_CACHE):
            self.embedding_model = SentenceTransformer(EMBEDDING_MODEL, cache_folder=EMBEDDING_CACHE)
        else:
            self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        self.index = None
        self.documents = []
        
        # Initialize OpenAI fallback and web scraper
        from src.openai_fallback.fallback import OpenAIFallback
        from src.web_scraper.scraper import WebScraper
        self.openai_fallback = OpenAIFallback()
        self.web_scraper = WebScraper()
        
    def build_index(self, documents: List[Dict[str, str]]):
        self.documents = documents
        texts = [doc["text"] for doc in documents]
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
        
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.astype('float32'))
        faiss.write_index(self.index, VECTOR_DB_PATH)
        
    def load_index(self):
        self.index = faiss.read_index(VECTOR_DB_PATH)
        
    def search(self, query: str, top_k: int = 3) -> List[str]:
        if not self.index or not self.documents:
            return []
        query_embedding = self.embedding_model.encode([query])
        distances, indices = self.index.search(query_embedding.astype('float32'), min(top_k, len(self.documents)))
        valid_results = []
        
        for idx in indices[0]:
            if 0 <= idx < len(self.documents):
                valid_results.append(self.documents[idx]["text"])
        return valid_results
    
    def add_document(self, document: Dict[str, str]):
        """Add a new document and rebuild index"""
        self.documents.append(document)
        self.rebuild_index()
    
    def rebuild_index(self):
        """Rebuild the FAISS index with current documents"""
        if not self.documents:
            return
        texts = [doc["text"] for doc in self.documents]
        embeddings = self.embedding_model.encode(texts)
        
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.astype('float32'))
        faiss.write_index(self.index, VECTOR_DB_PATH)
    
    
    
    def _correct_transcription(self, text: str) -> str:
        """Fix common Whisper mishearings"""
        corrections = {
            r'\btime more\b': 'tymor',
            r'\btime or\b': 'tymor',
            r'\btimer\b': 'tymor',
            r'\btimor\b': 'tymor',
            r'\btime mode\b': 'tymor',
            r'\btimeo\b': 'tymor',
            r'\btimeoot tech\b': 'tymor',
            r'\btime of\b': 'tymor',
            r'\btaimer\b': 'tymor',
            r'\btaimer\b': 'tymor',
            r'\bty mor\b': 'tymor',
        }
        import re
        for pattern, replacement in corrections.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text

    def answer_question(self, question: str) -> tuple[str, bool]:
        if not question:
            return "I didn't catch that. Could you repeat?", False
        
        question = self._correct_transcription(question)
        print(f"\n[QA Engine] Processing question: {question}")
        
        # Check for time/date questions - always use OpenAI
        time_keywords = ['what time', 'what date', 'today\'s date', 'current time', 'current date', 'what day', 'what is today']
        if any(keyword in question.lower() for keyword in time_keywords):
            print("[QA Engine] Time/date question detected - using OpenAI")
            if self.openai_fallback.enabled:
                context = self.web_scraper.search_web(question)
                answer = self.openai_fallback.get_answer(question, context)
                if answer:
                    return answer, True
        
        # Check for general conversational questions first
        from src.general.responses import GeneralResponses
        general = GeneralResponses()
        general_response = general.get_response(question)
        if general_response:
            print("[QA Engine] Using general response")
            return general_response, True
        
        if not self.documents or not self.index:
            print("[QA Engine] No local data available")
            if self.openai_fallback.enabled:
                print("[QA Engine] Calling OpenAI API with Serper context")
                context = self.web_scraper.search_web(question)
                answer = self.openai_fallback.get_answer(question, context)
                if answer:
                    return answer, True
            return "I don't have information about that. Could you teach me?", False
        
        # Check similarity threshold first
        query_embedding = self.embedding_model.encode([question])
        distances, indices = self.index.search(query_embedding.astype('float32'), 1)
        
        print(f"[QA Engine] Distance to nearest match: {distances[0][0] if len(distances[0]) > 0 else 'N/A'}")
        
        # Stricter threshold - only use local data if very similar
        if len(distances[0]) == 0 or distances[0][0] > 1.5:
            print("[QA Engine] No good local match found")
            if self.openai_fallback.enabled:
                print("[QA Engine] Calling OpenAI API with Serper context")
                context = self.web_scraper.search_web(question)
                answer = self.openai_fallback.get_answer(question, context)
                if answer:
                    return answer, True
            
            return "I don't have information about that. Could you teach me?", False
        
        print("[QA Engine] Using local knowledge base")
        relevant_docs = self.search(question, top_k=1)
        if not relevant_docs:
            return "I don't have information about that. Could you teach me?", False
        
        # Extract answer from Q&A format
        best_match = relevant_docs[0]
        
        # Check if the answer is actually relevant to the question
        question_lower = question.lower()
        answer_lower = best_match.lower()
        
        # Detect questions that need external knowledge
        external_keywords = ['competitor', 'alternative', 'versus', 'investor', 'funding', 'raised',
                             'vs', 'compare', 'better than', 'similar to', 'website','url','link','time', 'latest', 
                             'current', 'news', 'update', 'updates', 'reviews', 'feedback', 'famous', 'popular', 'trending']
        needs_external = any(keyword in question_lower for keyword in external_keywords)
        
        if needs_external:
            print("[QA Engine] Question needs external knowledge - using OpenAI")
            if self.openai_fallback.enabled:
                # Try web search first
                context = ""
                search_results = self.web_scraper.search_web(question)
                if search_results:
                    context = f"Web search results: {search_results}"
                    print(f"[QA Engine] Found web search results: {len(search_results)} chars")
                else:
                    # Fallback to website scraping
                    try:
                        scraped_docs = self.web_scraper.scrape_website()
                        if scraped_docs:
                            context = scraped_docs[0]['text'][:2000]
                    
                    except:
                        pass
                
                answer = self.openai_fallback.get_answer(question, context)
                if answer:
                    # Filter out apologetic responses
                    answer = self._clean_answer(answer)
                    return answer, True
        
        # If it's Q: A: format, extract just the answer
        if "A:" in best_match:
            answer_part = best_match.split("A:", 1)[1].strip()
            return answer_part, True
        
        # If it's CSV format with "answer:" field
        if "answer:" in best_match.lower():
            parts = best_match.split("answer:", 1)
            if len(parts) > 1:
                return parts[1].strip(), True
        
        # Otherwise return the best match
        return best_match, True
    
    def _clean_answer(self, answer: str) -> str:
        """Remove apologetic phrases and markdown formatting from OpenAI responses"""
        # Remove markdown formatting
        import re
        answer = re.sub(r'\*\*', '', answer)  # Remove **
        answer = re.sub(r'\*', '', answer)    # Remove *
        answer = re.sub(r'\n\d+\.\s', '. ', answer)  # Remove numbered lists
        answer = re.sub(r'\n-\s', '. ', answer)  # Remove bullet points
        answer = re.sub(r'\n+', ' ', answer)  # Remove newlines
        
        # Remove sentences containing apologetic patterns or date limitations
        patterns = [
            "i'm sorry",
            "i am sorry",
            "i apologize",
            "unfortunately",
            "i don't have access",
            "i do not have access",
            "i cannot",
            "i can't",
            "i do not have",
            "i don't have real-time",
            "i do not have real-time",
            "as of my last update",
            "my last update",
            "october 2023",
            "beyond october 2023"
        ]
        
        sentences = answer.replace('!', '.').replace('?', '.').split('.')
        filtered = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Check if sentence contains any apologetic pattern or date reference
            has_unwanted = any(pattern in sentence.lower() for pattern in patterns)
            
            if not has_unwanted:
                filtered.append(sentence)
        
        result = '. '.join(filtered)
        if result and not result.endswith('.'):
            result += '.'
        
        return result if result else "Check the official website for the latest information."

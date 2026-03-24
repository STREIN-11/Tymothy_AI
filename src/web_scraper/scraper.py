import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import os
from dotenv import load_dotenv
import urllib.parse

load_dotenv()

class WebScraper:
    def __init__(self):
        self.website_url = os.getenv('WEBSITE_URL', 'https://klutch.ai/')
    
    def scrape_website(self) -> List[Dict[str, str]]:
        """Scrape content from the website"""
        try:
            response = requests.get(self.website_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract text content
            text = soup.get_text(separator='\n', strip=True)
            
            # Create document from scraped content
            documents = [{
                "text": text,
                "source": "website_scrape"
            }]
            
            return documents
        except Exception as e:
            print(f"Error scraping website: {e}")
            return []
    
    def search_web(self, query: str) -> str:
        """Search web using Serper API (Google search results)"""
        serper_key = os.getenv('SERPER_API_KEY')
        if not serper_key or serper_key == 'your_serper_key_here':
            print("[Web Search] No Serper API key found")
            return ""
        
        try:
            url = "https://google.serper.dev/search"
            headers = {
                'X-API-KEY': serper_key,
                'Content-Type': 'application/json'
            }
            payload = {'q': query}
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            data = response.json()
            
            results = []
            
            # Get organic results
            for result in data.get('organic', [])[:3]:
                snippet = result.get('snippet', '')
                if snippet:
                    results.append(snippet)
            
            # Get knowledge graph if available
            if data.get('knowledgeGraph', {}).get('description'):
                results.insert(0, data['knowledgeGraph']['description'])
            
            return ' | '.join(results) if results else ""
        except Exception as e:
            print(f"Error searching web: {e}")
            return ""

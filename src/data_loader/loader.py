import csv
import json
import os
from typing import List, Dict

class DataLoader:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        
    def load_all_data(self) -> List[Dict[str, str]]:
        documents = []
        for filename in os.listdir(self.data_dir):
            filepath = os.path.join(self.data_dir, filename)
            if filename.endswith('.csv'):
                documents.extend(self._load_csv(filepath))
            elif filename.endswith('.txt'):
                documents.extend(self._load_txt(filepath))
            elif filename.endswith('.json'):
                documents.extend(self._load_json(filepath))
        return documents
    
    def _load_csv(self, filepath: str) -> List[Dict[str, str]]:
        documents = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                text = " ".join([f"{col}: {val}" for col, val in row.items()])
                documents.append({"text": text, "source": filepath})
        return documents
    
    def _load_txt(self, filepath: str) -> List[Dict[str, str]]:
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        documents = []
        lines = content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith('Q:'):
                question = line[2:].strip()
                i += 1
                if i < len(lines) and lines[i].strip().startswith('A:'):
                    answer = lines[i].strip()[2:].strip()
                    text = f"Q: {question} A: {answer}"
                    documents.append({"text": text, "source": filepath})
                i += 1
            elif line:
                documents.append({"text": line, "source": filepath})
                i += 1
            else:
                i += 1
        
        return documents
    
    def _load_json(self, filepath: str) -> List[Dict[str, str]]:
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        documents = []
        if isinstance(data, list):
            for item in data:
                text = json.dumps(item) if isinstance(item, dict) else str(item)
                documents.append({"text": text, "source": filepath})
        elif isinstance(data, dict):
            for key, value in data.items():
                text = f"{key}: {json.dumps(value) if isinstance(value, (dict, list)) else value}"
                documents.append({"text": text, "source": filepath})
        return documents

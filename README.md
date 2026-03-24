# Tymothy - Offline AI Assistant

An offline voice-activated AI assistant that responds to wake words and answers questions based on your custom data.

## Features
- 🎤 Wake word detection: "Hey Bob", "Hi Bob", "Bob"
- 📚 Knowledge base from CSV, TXT, JSON files
- 🔒 100% offline operation
- 🚀 Fast semantic search with FAISS

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Download Vosk Model
Download the small English model from: https://alphacephei.com/vosk/models
Extract to: `models/vosk-model-small-en-us-0.15/`

### 3. Add Your Data
Place your CSV, TXT, or JSON files in the `data/` directory.

**Example formats:**

`data/faq.csv`:
```csv
question,answer
What is your name?,My name is Bob
What can you do?,I can answer questions based on provided data
```

`data/info.txt`:
```
Q: What is your name?
A: My name is Bob, an offline AI assistant.

Q: How do you work?
A: I use semantic search to find answers from your data files.
```

`data/knowledge.json`:
```json
{
  "greeting": "Hello, I'm Bob",
  "purpose": "Answer questions from custom data"
}
```

### 4. Run Bob
```bash
python main.py
```

## Usage
1. Say "Hey Bob", "Hi Bob", or "Bob" to activate
2. Ask your question
3. Bob will search the knowledge base and respond

## Project Structure
```
Offline_Ai/
├── src/
│   ├── wake_word/       # Wake word detection
│   ├── qa_engine/       # Question answering engine
│   └── data_loader/     # Data ingestion
├── config/              # Configuration
├── data/                # Your data files (CSV, TXT, JSON)
├── models/              # AI models and vector database
├── tests/               # Unit tests
├── main.py              # Entry point
└── requirements.txt     # Dependencies
```

## Requirements
- Python 3.14.0
- Microphone access
- ~500MB disk space for models

# Tymor AI — Frontend

React + Three.js web interface for the Tymor AI assistant.

## Setup

```bash
cd frontend
npm install
npm start
```

Opens at http://localhost:3000

## Required: Place your GLB model

Copy `T_Character_Test.glb` into `frontend/public/`:

```
frontend/public/T_Character_Test.glb
```

## Usage

1. Start the Python backend first: `python main.py`
2. Start the frontend: `npm start`
3. Hold the 🎤 button (bottom-right) and speak
4. Release — the character will answer with lip sync

## Lip Sync

Driven by Web Audio API amplitude analysis on the response WAV.  
Works best if your GLB has morph targets named any of:
- `mouthOpen`, `jawOpen`, `viseme_aa`, `viseme_O`, `jawForward`

If none exist, the character will still animate (idle head bob) but without mouth movement.

## Architecture

```
Browser mic → SpeechRecognition (transcript)
           → POST /ask  → Python QA engine
           → GET /audio → WAV playback + lip sync on GLB
```

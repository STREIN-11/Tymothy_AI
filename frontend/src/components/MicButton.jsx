import React, { useState, useRef } from 'react';

const API = 'http://localhost:5000';

export default function MicButton({ onSpeakStart, onTranscript }) {
  const [state, setState] = useState('idle'); // idle | recording | thinking
  const recognitionRef = useRef(null);
  const transcriptRef = useRef('');

  const correctTranscript = (text) => {
    return text
      .replace(/\btime at technology\b/gi, 'Tymor Technology')
      .replace(/\btime at tech\b/gi, 'Tymor Technology')
      .replace(/\btime technology\b/gi, 'Tymor Technology')
      .replace(/\btime tech\b/gi, 'Tymor Technology')
      .replace(/\btime more\b/gi, 'Tymor')
      .replace(/\btime or\b/gi, 'Tymor')
      .replace(/\btimer\b/gi, 'Tymor')
      .replace(/\btimor\b/gi, 'Tymor')
      .replace(/\btime mode\b/gi, 'Tymor')
      .replace(/\btimeo\b/gi, 'Tymor')
      .replace(/\btime of\b/gi, 'Tymor')
      .replace(/\btaimer\b/gi, 'Tymor')
      .replace(/\bty mor\b/gi, 'Tymor')
      .replace(/\biot technology\b/gi, 'Tymor Technology')
      .replace(/\biot tech\b/gi, 'Tymor Technology');
  };

  const startRecording = () => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) {
      const text = prompt('Speech API not supported. Type your question:');
      if (text) submitQuestion(text);
      return;
    }
    transcriptRef.current = '';
    const rec = new SR();
    rec.lang = 'en-US';
    rec.continuous = true;
    rec.interimResults = true;
    rec.onresult = (e) => {
      transcriptRef.current = Array.from(e.results)
        .map((r) => r[0].transcript)
        .join(' ');
    };
    rec.onerror = () => setState('idle');
    recognitionRef.current = rec;
    rec.start();
    setState('recording');
  };

  const stopRecording = () => {
    recognitionRef.current?.stop();
    setState('thinking');
    // Give SR a moment to finalise
    setTimeout(() => {
      const text = transcriptRef.current.trim();
      if (text) submitQuestion(text);
      else setState('idle');
    }, 400);
  };

  const submitQuestion = async (text) => {
    onTranscript?.(correctTranscript(text));
    try {
      const res = await fetch(`${API}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: text }),
      });
      const data = await res.json();
      if (data.error) { setState('idle'); return; }

      // Audio is ready — /ask is now synchronous, fetch immediately
      const audioRes = await fetch(`${API}/audio?t=${Date.now()}`);
      if (!audioRes.ok) { setState('idle'); return; }
      const arrayBuf = await audioRes.arrayBuffer();
      const audioCtx = new AudioContext();
      const audioBuffer = await audioCtx.decodeAudioData(arrayBuf);

      onSpeakStart?.(audioBuffer, audioCtx, correctTranscript(data.answer));
    } catch (err) {
      console.error(err);
    } finally {
      setState('idle');
    }
  };

  return (
    <button
      onMouseDown={startRecording}
      onMouseUp={stopRecording}
      onTouchStart={(e) => { e.preventDefault(); startRecording(); }}
      onTouchEnd={(e) => { e.preventDefault(); stopRecording(); }}
      style={styles.btn(state)}
      title="Hold to speak"
    >
      {state === 'recording' ? '🔴' : state === 'thinking' ? '⏳' : '🎤'}
    </button>
  );
}

const styles = {
  btn: (state) => ({
    position: 'fixed',
    bottom: '24px',
    right: '24px',
    width: '52px',
    height: '52px',
    borderRadius: '50%',
    border: 'none',
    cursor: state === 'thinking' ? 'wait' : 'pointer',
    fontSize: '22px',
    background: state === 'recording'
      ? 'rgba(220,50,50,0.9)'
      : 'rgba(30,30,50,0.85)',
    boxShadow: state === 'recording'
      ? '0 0 0 4px rgba(220,50,50,0.4)'
      : '0 2px 12px rgba(0,0,0,0.5)',
    backdropFilter: 'blur(8px)',
    transition: 'all 0.2s',
    zIndex: 100,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  }),
};

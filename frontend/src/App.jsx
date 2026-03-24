import React, { useState, Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { Environment, OrbitControls } from '@react-three/drei';
import Character from './components/Character';
import MicButton from './components/MicButton';

export default function App() {
  const [speaking,    setSpeaking]    = useState(false);
  const [audioBuffer, setAudioBuffer] = useState(null);
  const [audioCtx,    setAudioCtx]    = useState(null);
  const [transcript,  setTranscript]  = useState('');
  const [answer,      setAnswer]      = useState('');

  const handleSpeakStart = (buf, ctx, text) => {
    setAudioBuffer(buf); setAudioCtx(ctx);
    setAnswer(text || ''); setSpeaking(true);
    setTimeout(() => setSpeaking(false), buf.duration * 1000 + 300);
  };

  return (
    <div style={{ width: '100vw', height: '100vh', position: 'relative' }}>
      <Canvas
        camera={{ fov: 45, near: 0.1, far: 100 }}
        style={{ background: 'radial-gradient(ellipse at center, #1a1a2e 0%, #0a0a0f 100%)' }}
        resize={{ scroll: false, debounce: { scroll: 50, resize: 0 } }}
      >
        <ambientLight intensity={0.5} />
        <directionalLight position={[2, 5, 3]}  intensity={1.2} castShadow />
        <directionalLight position={[-3, 2, -2]} intensity={0.3} color="#8080ff" />
        <pointLight       position={[0, 3, 2]}   intensity={0.4} color="#ffffff" />
        <Suspense fallback={null}>
          <Character isSpeaking={speaking} audioBuffer={audioBuffer} audioCtx={audioCtx} />
          <Environment preset="city" />
        </Suspense>
        <OrbitControls enablePan={false} minDistance={1} maxDistance={12}
          minPolarAngle={Math.PI / 6} maxPolarAngle={Math.PI / 1.6} />
      </Canvas>

      {(transcript || answer) && (
        <div style={styles.overlay}>
          {transcript && <p style={styles.question}>You: {transcript}</p>}
          {answer     && <p style={styles.answerText}>Tymor: {answer}</p>}
        </div>
      )}

      <MicButton onSpeakStart={handleSpeakStart} onTranscript={setTranscript} />
    </div>
  );
}

const styles = {
  overlay: {
    position:'fixed', bottom:'90px', right:'16px', maxWidth:'min(340px,90vw)',
    background:'rgba(10,10,20,0.78)', backdropFilter:'blur(12px)',
    borderRadius:'12px', padding:'12px 16px', color:'#fff',
    fontSize:'14px', lineHeight:1.5, zIndex:50,
    border:'1px solid rgba(255,255,255,0.08)',
  },
  question:   { color:'#aaa', marginBottom:'6px' },
  answerText: { color:'#e0e0ff' },
};

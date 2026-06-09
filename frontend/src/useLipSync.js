import { useRef, useCallback } from 'react';

export function useLipSync() {
  const analyserRef = useRef(null);
  const dataArrayRef = useRef(null);
  const sourceRef = useRef(null);

  const startLipSync = useCallback((audioBuffer, audioCtx) => {
    if (!audioBuffer || !audioCtx) return;

    try {
      if (sourceRef.current) {
        try { sourceRef.current.stop(); } catch (e) {}
        try { sourceRef.current.disconnect(); } catch (e) {}
        sourceRef.current = null;
      }
      if (analyserRef.current) {
        try { analyserRef.current.disconnect(); } catch (e) {}
        analyserRef.current = null;
      }

      const analyser = audioCtx.createAnalyser();
      analyser.fftSize = 512;
      analyser.smoothingTimeConstant = 0.6;

      const source = audioCtx.createBufferSource();
      source.buffer = audioBuffer;

      source.connect(audioCtx.destination);
      source.connect(analyser);

      const dataArray = new Uint8Array(analyser.frequencyBinCount);
      analyserRef.current = analyser;
      dataArrayRef.current = dataArray;
      sourceRef.current = source;

      source.onended = () => {
        analyserRef.current = null;
        dataArrayRef.current = null;
        sourceRef.current = null;
        console.log('[LipSync] audio ended');
      };

      source.start(0);
      console.log('[LipSync] started');
    } catch (err) {
      console.error('[LipSync] start failed:', err);
    }
  }, []);

  const getMouthValue = useCallback(() => {
    const analyser = analyserRef.current;
    const dataArray = dataArrayRef.current;
    if (!analyser || !dataArray) return 0;

    analyser.getByteFrequencyData(dataArray);

    const sampleRate = analyser.context.sampleRate;
    const binHz = sampleRate / analyser.fftSize;
    const lo = Math.floor(80 / binHz);
    const hi = Math.min(Math.floor(3000 / binHz), dataArray.length - 1);

    let sum = 0;
    for (let i = lo; i <= hi; i++) sum += dataArray[i];
    const avg = sum / (hi - lo + 1);

    // map 20-160 range → 0-1
    return Math.min(1, Math.max(0, (avg - 20) / 140));
  }, []);

  return { startLipSync, getMouthValue };
}

import { useRef, useCallback } from 'react';

export function useLipSync() {
  const analyserRef = useRef(null);
  const dataArrayRef = useRef(null);
  const sourceRef = useRef(null);

  const startLipSync = useCallback((audioBuffer, audioCtx) => {
    if (!audioBuffer || !audioCtx) return;

    try {
      if (sourceRef.current) {
        try {
          sourceRef.current.stop();
        } catch (e) {}
        try {
          sourceRef.current.disconnect();
        } catch (e) {}
        sourceRef.current = null;
      }

      const analyser = audioCtx.createAnalyser();
      analyser.fftSize = 1024;
      analyser.smoothingTimeConstant = 0.8;

      const source = audioCtx.createBufferSource();
      source.buffer = audioBuffer;

      // play sound normally
      source.connect(audioCtx.destination);

      // analyze in parallel
      source.connect(analyser);

      const dataArray = new Uint8Array(analyser.fftSize);

      analyserRef.current = analyser;
      dataArrayRef.current = dataArray;
      sourceRef.current = source;

      source.onended = () => {
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

    analyser.getByteTimeDomainData(dataArray);

    let sum = 0;
    for (let i = 0; i < dataArray.length; i += 1) {
      const normalized = (dataArray[i] - 128) / 128;
      sum += normalized * normalized;
    }

    const rms = Math.sqrt(sum / dataArray.length);

    let value = rms * 12;

    if (value < 0.02) value = 0;
    if (value > 1) value = 1;

    return value;
  }, []);

  return {
    startLipSync,
    getMouthValue,
  };
}
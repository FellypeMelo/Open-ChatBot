import { useCallback, useRef } from 'react';

export const useAudio = () => {
  const audioCtxRef = useRef<AudioContext | null>(null);

  const resumeAudio = useCallback(async () => {
    if (audioCtxRef.current?.state === 'suspended') {
      await audioCtxRef.current.resume();
    }
  }, []);

  const playTypewriterClick = useCallback(() => {
    try {
      if (!audioCtxRef.current) {
        audioCtxRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
      }

      const ctx = audioCtxRef.current;
      if (ctx.state === 'suspended') {
        ctx.resume();
      }

      const oscillator = ctx.createOscillator();
      const gainNode = ctx.createGain();

      // Soft mechanical click sound
      oscillator.type = 'sine';
      oscillator.frequency.setValueAtTime(150 + Math.random() * 50, ctx.currentTime);
      oscillator.frequency.exponentialRampToValueAtTime(40, ctx.currentTime + 0.05);

      gainNode.gain.setValueAtTime(0.05, ctx.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.05);

      oscillator.connect(gainNode);
      gainNode.connect(ctx.destination);

      oscillator.start();
      oscillator.stop(ctx.currentTime + 0.05);
    } catch (e) {
      // Audio might be blocked or not supported
      console.warn('Audio playback failed', e);
    }
  }, []);

  return { playTypewriterClick, resumeAudio };
};

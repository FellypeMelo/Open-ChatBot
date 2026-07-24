import { useCallback, useRef } from 'react';

export const useAudio = () => {
  const audioCtxRef = useRef<AudioContext | null>(null);
  const ambientSourceRef = useRef<AudioBufferSourceNode | null>(null);
  const currentLocationRef = useRef<string>('');
  // The typewriter releases a character (and calls this) up to ~50x/sec while
  // draining a token buffer, and each call used to build+tear down a fresh
  // oscillator/gain graph -- audio-thread/GC churn for no perceptible gain.
  // Playing every other tick halves that churn while keeping a near-identical
  // audible cadence.
  const clickCountRef = useRef(0);

  const resumeAudio = useCallback(async () => {
    if (audioCtxRef.current?.state === 'suspended') {
      await audioCtxRef.current.resume();
    }
  }, []);

  const playTypewriterClick = useCallback(() => {
    clickCountRef.current += 1;
    if (clickCountRef.current % 2 === 0) return;
    try {
      if (!audioCtxRef.current) {
        audioCtxRef.current = new (window.AudioContext || (window as typeof window & { webkitAudioContext?: typeof AudioContext }).webkitAudioContext)();
      }

      const ctx = audioCtxRef.current;
      if (ctx.state === 'suspended') {
        ctx.resume();
      }

      const oscillator = ctx.createOscillator();
      const gainNode = ctx.createGain();

      // Soft mechanical tick sound (shorter, higher, and much quieter)
      oscillator.type = 'triangle';
      oscillator.frequency.setValueAtTime(900 + Math.random() * 200, ctx.currentTime);
      oscillator.frequency.exponentialRampToValueAtTime(150, ctx.currentTime + 0.012);

      gainNode.gain.setValueAtTime(0.006, ctx.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.012);

      oscillator.connect(gainNode);
      gainNode.connect(ctx.destination);

      oscillator.start();
      oscillator.stop(ctx.currentTime + 0.015);
    } catch (e) {
      console.warn('Audio playback failed', e);
    }
  }, []);

  const stopAmbient = useCallback(() => {
    if (ambientSourceRef.current) {
      try {
        ambientSourceRef.current.stop();
      } catch {
        // Suppress error
      }
      ambientSourceRef.current = null;
    }
    currentLocationRef.current = '';
  }, []);

  const playAmbient = useCallback((location: string) => {
    try {
      const loc = (location || 'Living Room').trim().toLowerCase();
      if (currentLocationRef.current === loc) return;
      currentLocationRef.current = loc;

      if (!audioCtxRef.current) {
        audioCtxRef.current = new (window.AudioContext || (window as typeof window & { webkitAudioContext?: typeof AudioContext }).webkitAudioContext)();
      }
      const ctx = audioCtxRef.current;
      if (ctx.state === 'suspended') {
        ctx.resume();
      }

      // Stop previous ambient sound if playing
      if (ambientSourceRef.current) {
        try {
          ambientSourceRef.current.stop();
        } catch {
          // Suppress error
        }
      }

      // Generate a 4-second buffer of brown noise (softer and deeper than white noise)
      const bufferSize = ctx.sampleRate * 4;
      const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
      const data = buffer.getChannelData(0);
      let lastOut = 0.0;
      for (let i = 0; i < bufferSize; i++) {
        const white = Math.random() * 2 - 1;
        data[i] = (lastOut + (0.02 * white)) / 1.02;
        lastOut = data[i];
        data[i] *= 3.5; // Compensate for loss of volume
      }

      const noiseNode = ctx.createBufferSource();
      noiseNode.buffer = buffer;
      noiseNode.loop = true;

      // Filter settings based on location to synthesize atmospheric sounds
      const filter = ctx.createBiquadFilter();
      const gainNode = ctx.createGain();

      if (loc.includes('garden') || loc.includes('outdoor') || loc.includes('park') || loc.includes('forest')) {
        // Soft wind: Bandpass filter with a low frequency
        filter.type = 'bandpass';
        filter.frequency.value = 350;
        filter.Q.value = 1.0;
        gainNode.gain.value = 0.005; // Much quieter, softer
      } else if (loc.includes('rain') || loc.includes('storm') || loc.includes('outside')) {
        // Rain sound: High-pass filter for crackling rain drops
        filter.type = 'highpass';
        filter.frequency.value = 800;
        gainNode.gain.value = 0.003;
      } else {
        // Living room / Room tone: Cozy deep lowpass hum
        filter.type = 'lowpass';
        filter.frequency.value = 100;
        gainNode.gain.value = 0.006;
      }

      noiseNode.connect(filter);
      filter.connect(gainNode);
      gainNode.connect(ctx.destination);

      noiseNode.start();
      ambientSourceRef.current = noiseNode;
    } catch (e) {
      console.warn('Ambient playback failed', e);
    }
  }, []);

  return { playTypewriterClick, resumeAudio, playAmbient, stopAmbient };
};

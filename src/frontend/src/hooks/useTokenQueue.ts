import { useState, useRef, useEffect, useCallback } from 'react';

// Above this many buffered characters, release more than one per tick so a
// fast-streaming model can't leave the typewriter visibly draining seconds
// after generation actually finished. Below it, release exactly one char per
// tick (the original steady cadence) for small/normal buffers.
const CATCH_UP_DIVISOR = 10;

/**
 * A hook that manages a queue of tokens (characters or strings) and releases them
 * at a steady, smoothed rate to create a fluid "typing" effect.
 *
 * @param msPerToken The time in milliseconds between each token release.
 * @param onTokenReleased Optional callback triggered every time a token release batch fires.
 * @returns An object containing the displayed content, enqueue/reset functions, and streaming state.
 */
export const useTokenQueue = (msPerToken: number = 25, onTokenReleased?: () => void) => {
  const [displayedContent, setDisplayedContent] = useState('');
  const [isDraining, setIsDraining] = useState(false);
  const bufferRef = useRef<string[]>([]);
  const intervalRef = useRef<number | null>(null);

  const startInterval = useCallback(() => {
    if (intervalRef.current !== null) return;

    setIsDraining(true);
    intervalRef.current = window.setInterval(() => {
      const buffer = bufferRef.current;
      if (buffer.length > 0) {
        // Proportional to the current backlog so a burst of tokens catches
        // up instead of the display lagging arbitrarily far behind.
        const releaseCount = Math.max(1, Math.ceil(buffer.length / CATCH_UP_DIVISOR));
        const released = buffer.splice(0, releaseCount);
        setDisplayedContent(prev => prev + released.join(''));
        if (onTokenReleased) onTokenReleased();
      } else {
        if (intervalRef.current !== null) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
        setIsDraining(false);
      }
    }, msPerToken);
  }, [msPerToken, onTokenReleased]);

  const enqueue = useCallback((tokens: string) => {
    if (!tokens) return;
    // Split into characters for smooth character-by-character typing
    bufferRef.current.push(...tokens.split(''));
    startInterval();
  }, [startInterval]);

  const reset = useCallback(() => {
    setDisplayedContent('');
    bufferRef.current = [];
    if (intervalRef.current !== null) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setIsDraining(false);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current !== null) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  return { 
    displayedContent, 
    enqueue, 
    reset, 
    isDraining 
  };
};

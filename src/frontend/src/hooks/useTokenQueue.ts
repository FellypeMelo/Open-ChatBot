import { useState, useRef, useEffect, useCallback } from 'react';

/**
 * A hook that manages a queue of tokens (characters or strings) and releases them
 * at a steady, smoothed rate to create a fluid "typing" effect.
 * 
 * @param msPerToken The time in milliseconds between each token release.
 * @param onTokenReleased Optional callback triggered every time a token is released.
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
      if (bufferRef.current.length > 0) {
        const nextToken = bufferRef.current.shift();
        if (nextToken !== undefined) {
          setDisplayedContent(prev => prev + nextToken);
          if (onTokenReleased) onTokenReleased();
        }
      } else {
        if (intervalRef.current !== null) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
        setIsDraining(false);
      }
    }, msPerToken);
  }, [msPerToken]);

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

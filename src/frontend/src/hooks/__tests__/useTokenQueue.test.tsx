import { renderHook, act } from '@testing-library/react';
import { useTokenQueue } from '../useTokenQueue';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

describe('useTokenQueue', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('should start empty', () => {
    const { result } = renderHook(() => useTokenQueue(50));
    expect(result.current.displayedContent).toBe('');
    expect(result.current.isDraining).toBe(false);
  });

  it('should release tokens at a steady rate', () => {
    const { result } = renderHook(() => useTokenQueue(100));
    
    act(() => {
      result.current.enqueue('ABC');
    });

    expect(result.current.isDraining).toBe(true);
    expect(result.current.displayedContent).toBe(''); // Initially empty until first interval

    act(() => {
      vi.advanceTimersByTime(100);
    });
    expect(result.current.displayedContent).toBe('A');

    act(() => {
      vi.advanceTimersByTime(100);
    });
    expect(result.current.displayedContent).toBe('AB');

    act(() => {
      vi.advanceTimersByTime(100);
    });
    expect(result.current.displayedContent).toBe('ABC');
    expect(result.current.isDraining).toBe(false);
  });

  it('should allow enqueuing more tokens while draining', () => {
    const { result } = renderHook(() => useTokenQueue(100));
    
    act(() => {
      result.current.enqueue('A');
    });

    act(() => {
      vi.advanceTimersByTime(100);
    });
    expect(result.current.displayedContent).toBe('A');

    act(() => {
      result.current.enqueue('B');
    });

    act(() => {
      vi.advanceTimersByTime(100);
    });
    expect(result.current.displayedContent).toBe('AB');
  });

  it('should reset correctly', () => {
    const { result } = renderHook(() => useTokenQueue(100));
    
    act(() => {
      result.current.enqueue('ABC');
      vi.advanceTimersByTime(100);
    });
    expect(result.current.displayedContent).toBe('A');

    act(() => {
      result.current.reset();
    });

    expect(result.current.displayedContent).toBe('');
    expect(result.current.isDraining).toBe(false);

    act(() => {
      vi.advanceTimersByTime(100);
    });
    expect(result.current.displayedContent).toBe(''); // Should not continue
  });
});

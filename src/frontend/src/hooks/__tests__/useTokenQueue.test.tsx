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
    
    // One more tick to clear the interval and stop draining
    act(() => {
      vi.advanceTimersByTime(100);
    });
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

  it('releases more than one character per tick once the buffer backs up, catching up instead of lagging indefinitely', () => {
    const { result } = renderHook(() => useTokenQueue(20));
    const longText = 'x'.repeat(40);

    act(() => {
      result.current.enqueue(longText);
    });

    act(() => {
      vi.advanceTimersByTime(20);
    });
    // A 40-char backlog must release more than one char on the very first
    // tick -- the old implementation always released exactly one, regardless
    // of how far behind the buffer had fallen.
    expect(result.current.displayedContent.length).toBeGreaterThan(1);

    act(() => {
      vi.advanceTimersByTime(20 * 30);
    });
    expect(result.current.displayedContent).toBe(longText);
    expect(result.current.isDraining).toBe(false);
  });

  it('still releases exactly one character per tick for a small buffer (unchanged steady cadence)', () => {
    const { result } = renderHook(() => useTokenQueue(50));

    act(() => {
      result.current.enqueue('Hi');
    });

    act(() => {
      vi.advanceTimersByTime(50);
    });
    expect(result.current.displayedContent).toBe('H');

    act(() => {
      vi.advanceTimersByTime(50);
    });
    expect(result.current.displayedContent).toBe('Hi');
  });
});

import { renderHook } from '@testing-library/react';
import { useAtmosphere } from '../useAtmosphere';
import { describe, it, expect } from 'vitest';

describe('useAtmosphere', () => {
  it('should return speech atmosphere by default when text is empty', () => {
    const { result } = renderHook(() => useAtmosphere(''));
    expect(result.current).toEqual({
      blurAmount: 0,
      textOpacity: 1,
      blockType: 'speech',
    });
  });

  it('should detect thought block when odd number of single asterisks exist', () => {
    const { result } = renderHook(() => useAtmosphere('This is a *thought'));
    expect(result.current).toEqual({
      blurAmount: 8,
      textOpacity: 0.7,
      blockType: 'thought',
    });
  });

  it('should detect speech block when single asterisks are balanced', () => {
    const { result } = renderHook(() => useAtmosphere('This is a *thought* and this is speech'));
    expect(result.current).toEqual({
      blurAmount: 0,
      textOpacity: 1,
      blockType: 'speech',
    });
  });

  it('should detect action block when odd number of double asterisks exist', () => {
    const { result } = renderHook(() => useAtmosphere('This is an **action'));
    expect(result.current).toEqual({
      blurAmount: 2,
      textOpacity: 1,
      blockType: 'action',
    });
  });

  it('should detect speech block when double asterisks are balanced', () => {
    const { result } = renderHook(() => useAtmosphere('This is an **action** and now speech'));
    expect(result.current).toEqual({
      blurAmount: 0,
      textOpacity: 1,
      blockType: 'speech',
    });
  });

  it('should prioritize the last unclosed block type correctly', () => {
    const { result: actionResult } = renderHook(() => useAtmosphere('Some *thought* then **action'));
    expect(actionResult.current.blockType).toBe('action');

    const { result: thoughtResult } = renderHook(() => useAtmosphere('Some **action** then *thought'));
    expect(thoughtResult.current.blockType).toBe('thought');
  });

  // Incremental-scan regression coverage: the hook now tracks marker state
  // across appends instead of re-scanning the whole string each call, so it
  // must classify correctly even when a "**" marker is split across two
  // separate appends (as happens once tokens stream in one character at a
  // time via the typewriter).
  it('classifies correctly across repeated appends, including a double-star marker split across two updates', () => {
    const { result, rerender } = renderHook(({ text }) => useAtmosphere(text), {
      initialProps: { text: 'Hello ' },
    });
    expect(result.current.blockType).toBe('speech');

    rerender({ text: 'Hello *' });
    expect(result.current.blockType).toBe('thought');

    // The second '*' lands in a separate append, completing a "**" pair
    // whose two characters spanned two different calls.
    rerender({ text: 'Hello **' });
    expect(result.current.blockType).toBe('action');

    rerender({ text: 'Hello **action' });
    expect(result.current.blockType).toBe('action');

    rerender({ text: 'Hello **action**' });
    expect(result.current.blockType).toBe('speech');

    rerender({ text: 'Hello **action** then *thought' });
    expect(result.current.blockType).toBe('thought');
  });

  it('resets its incremental state when the text is replaced by a new (shorter) message', () => {
    const { result, rerender } = renderHook(({ text }) => useAtmosphere(text), {
      initialProps: { text: 'An unclosed *thought' },
    });
    expect(result.current.blockType).toBe('thought');

    // Simulates useTokenQueue's reset() -> displayedContent goes back to ''
    // for the next message rather than continuing to grow.
    rerender({ text: '' });
    expect(result.current.blockType).toBe('speech');

    rerender({ text: 'Fresh reply' });
    expect(result.current.blockType).toBe('speech');
  });

  it('returns a referentially stable result across renders while the block type is unchanged', () => {
    const { result, rerender } = renderHook(({ text }) => useAtmosphere(text), {
      initialProps: { text: 'Hello' },
    });
    const first = result.current;

    rerender({ text: 'Hello wor' });

    expect(result.current).toBe(first);
    expect(result.current.blockType).toBe('speech');
  });
});

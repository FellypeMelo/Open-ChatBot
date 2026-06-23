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
});

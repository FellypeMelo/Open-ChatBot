import { renderHook, act } from '@testing-library/react';
import { useSettings } from '../useSettings';
import { describe, it, expect, beforeEach, vi } from 'vitest';

describe('useSettings', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  it('should initialize with default values if localStorage is empty', () => {
    const { result } = renderHook(() => useSettings());
    expect(result.current.config).toEqual({
      base_url: 'http://localhost:8080',
      model_name: '',
    });
  });

  it('should initialize with values from localStorage if they exist', () => {
    const savedConfig = {
      base_url: 'http://api.example.com',
      model_name: 'test-model',
    };
    localStorage.setItem('llm_config', JSON.stringify(savedConfig));

    const { result } = renderHook(() => useSettings());
    expect(result.current.config).toEqual(savedConfig);
  });

  it('should update localStorage when config changes', () => {
    const { result } = renderHook(() => useSettings());
    const newConfig = {
      base_url: 'http://new-url:1234',
      model_name: 'new-model',
    };

    act(() => {
      result.current.setConfig(newConfig);
    });

    expect(result.current.config).toEqual(newConfig);
    expect(JSON.parse(localStorage.getItem('llm_config') || '{}')).toEqual(newConfig);
  });

  it('should fall back to default values if localStorage contains invalid JSON', () => {
    localStorage.setItem('llm_config', 'invalid-json{');
    
    // Suppress console.error for this test as we expect a parse error
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    
    const { result } = renderHook(() => useSettings());
    
    expect(result.current.config).toEqual({
      base_url: 'http://localhost:8080',
      model_name: '',
    });
    expect(consoleSpy).toHaveBeenCalled();
    
    consoleSpy.mockRestore();
  });
});

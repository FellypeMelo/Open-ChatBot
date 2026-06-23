import { renderHook, act } from '@testing-library/react';
import { useAudio } from '../useAudio';
import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';

describe('useAudio', () => {
  let mockAudioContextInstance: any;
  let mockOscillator: any;
  let mockGain: any;
  let mockBiquadFilter: any;
  let mockBufferSource: any;

  beforeEach(() => {
    vi.clearAllMocks();

    mockOscillator = {
      type: '',
      frequency: {
        setValueAtTime: vi.fn(),
        exponentialRampToValueAtTime: vi.fn(),
      },
      connect: vi.fn(),
      start: vi.fn(),
      stop: vi.fn(),
    };

    mockGain = {
      gain: {
        value: 0,
        setValueAtTime: vi.fn(),
        exponentialRampToValueAtTime: vi.fn(),
      },
      connect: vi.fn(),
    };

    mockBiquadFilter = {
      type: '',
      frequency: { value: 0 },
      Q: { value: 0 },
      connect: vi.fn(),
    };

    mockBufferSource = {
      buffer: null,
      loop: false,
      connect: vi.fn(),
      start: vi.fn(),
      stop: vi.fn(),
    };

    mockAudioContextInstance = {
      state: 'suspended',
      currentTime: 0,
      sampleRate: 44100,
      resume: vi.fn().mockImplementation(async () => {
        mockAudioContextInstance.state = 'running';
      }),
      createOscillator: vi.fn().mockReturnValue(mockOscillator),
      createGain: vi.fn().mockReturnValue(mockGain),
      createBiquadFilter: vi.fn().mockReturnValue(mockBiquadFilter),
      createBufferSource: vi.fn().mockReturnValue(mockBufferSource),
      createBuffer: vi.fn().mockImplementation((channels, size, rate) => ({
        getChannelData: vi.fn().mockReturnValue(new Float32Array(size)),
        sampleRate: rate,
      })),
      destination: {},
    };

    // Set mock AudioContext on window
    (window as any).AudioContext = vi.fn().mockImplementation(function() {
      return mockAudioContextInstance;
    });
  });

  afterEach(() => {
    delete (window as any).AudioContext;
  });

  it('should resume audio context if suspended', async () => {
    const { result } = renderHook(() => useAudio());
    
    // Trigger typewriter click once to instantiate the context
    act(() => {
      result.current.playTypewriterClick();
    });

    await act(async () => {
      await result.current.resumeAudio();
    });

    expect(mockAudioContextInstance.resume).toHaveBeenCalled();
    expect(mockAudioContextInstance.state).toBe('running');
  });

  it('should play typewriter click oscillator sound', () => {
    const { result } = renderHook(() => useAudio());

    act(() => {
      result.current.playTypewriterClick();
    });

    expect(window.AudioContext).toHaveBeenCalled();
    expect(mockAudioContextInstance.createOscillator).toHaveBeenCalled();
    expect(mockAudioContextInstance.createGain).toHaveBeenCalled();
    expect(mockOscillator.start).toHaveBeenCalled();
    expect(mockOscillator.stop).toHaveBeenCalled();
  });

  it('should play and synthesize ambient noise based on location', () => {
    const { result } = renderHook(() => useAudio());

    // 1. Test Living Room / Room tone (default lowpass hum)
    act(() => {
      result.current.playAmbient('Living Room');
    });

    expect(mockAudioContextInstance.createBufferSource).toHaveBeenCalled();
    expect(mockAudioContextInstance.createBiquadFilter).toHaveBeenCalled();
    expect(mockBiquadFilter.type).toBe('lowpass');
    expect(mockBiquadFilter.frequency.value).toBe(100);
    expect(mockBufferSource.start).toHaveBeenCalled();

    // 2. Test Outdoor/Garden (bandpass wind)
    act(() => {
      result.current.playAmbient('Garden');
    });
    expect(mockBiquadFilter.type).toBe('bandpass');
    expect(mockBiquadFilter.frequency.value).toBe(350);

    // 3. Test Rain/Storm (highpass crackle)
    act(() => {
      result.current.playAmbient('Rainy Streets');
    });
    expect(mockBiquadFilter.type).toBe('highpass');
    expect(mockBiquadFilter.frequency.value).toBe(800);
  });

  it('should stop ambient playback and clear location reference', () => {
    const { result } = renderHook(() => useAudio());

    act(() => {
      result.current.playAmbient('Garden');
    });

    act(() => {
      result.current.stopAmbient();
    });

    expect(mockBufferSource.stop).toHaveBeenCalled();
  });

  it('should handle errors gracefully during playback and context setup', () => {
    (window as any).AudioContext = vi.fn().mockImplementation(() => {
      throw new Error('AudioContext failed to initialize');
    });

    const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
    const { result } = renderHook(() => useAudio());

    act(() => {
      result.current.playTypewriterClick();
      result.current.playAmbient('Garden');
    });

    expect(consoleSpy).toHaveBeenCalled();
    consoleSpy.mockRestore();
  });
});

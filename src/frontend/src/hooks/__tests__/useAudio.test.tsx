import { renderHook, act } from '@testing-library/react';
import { useAudio } from '../useAudio';
import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';

interface MockOscillator {
  type: string;
  frequency: {
    setValueAtTime: ReturnType<typeof vi.fn>;
    exponentialRampToValueAtTime: ReturnType<typeof vi.fn>;
  };
  connect: ReturnType<typeof vi.fn>;
  start: ReturnType<typeof vi.fn>;
  stop: ReturnType<typeof vi.fn>;
}

interface MockGain {
  gain: {
    value: number;
    setValueAtTime: ReturnType<typeof vi.fn>;
    exponentialRampToValueAtTime: ReturnType<typeof vi.fn>;
  };
  connect: ReturnType<typeof vi.fn>;
}

interface MockBiquadFilter {
  type: string;
  frequency: { value: number };
  Q: { value: number };
  connect: ReturnType<typeof vi.fn>;
}

interface MockBufferSource {
  buffer: AudioBuffer | null;
  loop: boolean;
  connect: ReturnType<typeof vi.fn>;
  start: ReturnType<typeof vi.fn>;
  stop: ReturnType<typeof vi.fn>;
}

interface MockAudioContextInstance {
  state: string;
  currentTime: number;
  sampleRate: number;
  resume: ReturnType<typeof vi.fn>;
  createOscillator: ReturnType<typeof vi.fn>;
  createGain: ReturnType<typeof vi.fn>;
  createBiquadFilter: ReturnType<typeof vi.fn>;
  createBufferSource: ReturnType<typeof vi.fn>;
  createBuffer: ReturnType<typeof vi.fn>;
  destination: Record<string, unknown>;
}

describe('useAudio', () => {
  let mockAudioContextInstance: MockAudioContextInstance;
  let mockOscillator: MockOscillator;
  let mockGain: MockGain;
  let mockBiquadFilter: MockBiquadFilter;
  let mockBufferSource: MockBufferSource;

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
    (window as typeof window & { AudioContext?: ReturnType<typeof vi.fn> }).AudioContext = vi.fn().mockImplementation(function(this: unknown) {
      return mockAudioContextInstance;
    });
  });

  afterEach(() => {
    delete (window as typeof window & { AudioContext?: ReturnType<typeof vi.fn> }).AudioContext;
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
    (window as typeof window & { AudioContext?: ReturnType<typeof vi.fn> }).AudioContext = vi.fn().mockImplementation(() => {
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

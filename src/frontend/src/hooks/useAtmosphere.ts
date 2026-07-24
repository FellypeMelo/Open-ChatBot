import { useState } from 'react';

export type BlockType = 'speech' | 'thought' | 'action';

export interface Atmosphere {
  blurAmount: number;
  textOpacity: number;
  blockType: BlockType;
}

// Module-level constants -- one fixed object per block type, so returning
// the same type twice in a row naturally yields the same object reference
// (no per-render allocation, no manual memoization needed).
const ATMOSPHERE_BY_TYPE: Record<BlockType, Atmosphere> = {
  thought: { blurAmount: 8, textOpacity: 0.7, blockType: 'thought' }, // Deep blur for internal thoughts
  action: { blurAmount: 2, textOpacity: 1, blockType: 'action' }, // Slight focus blur for actions
  speech: { blurAmount: 0, textOpacity: 1, blockType: 'speech' },
};

type RunType = 'double' | 'single' | null;

interface RunState {
  processedLength: number;
  // Counts of *closed* runs only -- a run still open at the end of `text`
  // (more '*'s may still be streamed in) is tracked separately below and
  // folded in provisionally when deriving the current block type.
  sealedDoubleCount: number;
  sealedSingleCount: number;
  openRunLength: number;
  lastSealedRunType: RunType;
}

const createRunState = (): RunState => ({
  processedLength: 0,
  sealedDoubleCount: 0,
  sealedSingleCount: 0,
  openRunLength: 0,
  lastSealedRunType: null,
});

// Advances the run-tracking state machine over one appended delta. A run is
// a maximal sequence of consecutive '*' characters:
//  - a run of length >= 2 contributes floor(length / 2) to the "action"
//    (double-star) count -- equivalent to the original text.match(/\*\*/g).
//  - a run of length === 1 contributes 1 to the "thought" (single-star)
//    count -- equivalent to the original negative-lookaround regex.
// This mirrors the original whole-string regex scan exactly, but only ever
// looks at the newly appended characters (O(delta) instead of O(text)).
const applyDelta = (state: RunState, delta: string): RunState => {
  let { sealedDoubleCount, sealedSingleCount, openRunLength, lastSealedRunType } = state;
  for (let i = 0; i < delta.length; i++) {
    if (delta[i] === '*') {
      openRunLength += 1;
    } else if (openRunLength > 0) {
      if (openRunLength >= 2) {
        sealedDoubleCount += Math.floor(openRunLength / 2);
        lastSealedRunType = 'double';
      } else {
        sealedSingleCount += 1;
        lastSealedRunType = 'single';
      }
      openRunLength = 0;
    }
  }
  return {
    processedLength: state.processedLength + delta.length,
    sealedDoubleCount,
    sealedSingleCount,
    openRunLength,
    lastSealedRunType,
  };
};

const deriveBlockType = (state: RunState): BlockType => {
  let doubleCount = state.sealedDoubleCount;
  let singleCount = state.sealedSingleCount;
  let lastRunType = state.lastSealedRunType;

  if (state.openRunLength > 0) {
    if (state.openRunLength >= 2) {
      doubleCount += Math.floor(state.openRunLength / 2);
      lastRunType = 'double';
    } else {
      singleCount += 1;
      lastRunType = 'single';
    }
  }

  if (lastRunType === 'double') {
    return doubleCount % 2 !== 0 ? 'action' : 'speech';
  }
  if (lastRunType === 'single') {
    return singleCount % 2 !== 0 ? 'thought' : 'speech';
  }
  return 'speech';
};

export const useAtmosphere = (text: string): Atmosphere => {
  // "Adjust state during render" (react.dev's sanctioned pattern for
  // deriving state from a changed prop) rather than a mutated ref, so the
  // incremental scan state survives across renders without ever touching
  // `.current` mid-render.
  const [state, setState] = useState<RunState>(createRunState);

  let nextState = state;
  // A shorter (or reset-to-empty) text means a new message started --
  // `text` is no longer an extension of what we already scanned.
  if (text.length < nextState.processedLength) {
    nextState = createRunState();
  }
  if (text.length > nextState.processedLength) {
    nextState = applyDelta(nextState, text.slice(nextState.processedLength));
  }
  if (nextState !== state) {
    setState(nextState);
  }

  return ATMOSPHERE_BY_TYPE[deriveBlockType(nextState)];
};

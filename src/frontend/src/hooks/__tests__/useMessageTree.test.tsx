import { renderHook, act } from '@testing-library/react';
import { useMessageTree } from '../useMessageTree';
import type { MessageNode } from '../useMessageTree';
import { describe, it, expect } from 'vitest';

describe('useMessageTree', () => {
  const mockNodes: MessageNode[] = [
    { id: 1, parent_id: null, role: 'user', content: 'Hello', variant_index: 0 },
    { id: 2, parent_id: 1, role: 'assistant', content: 'Hi v1', variant_index: 0 },
    { id: 3, parent_id: 1, role: 'assistant', content: 'Hi v2', variant_index: 1 },
    { id: 4, parent_id: 2, role: 'user', content: 'How are you?', variant_index: 0 },
    { id: 5, parent_id: 3, role: 'user', content: 'What is up?', variant_index: 0 },
  ];

  it('should compute the default active path (latest variants)', () => {
    const { result } = renderHook(() => useMessageTree(mockNodes));
    
    // Default path should follow id 1 -> id 3 -> id 5 (since 3 is the latest variant of 1's children)
    expect(result.current.activePath.map(n => n.id)).toEqual([1, 3, 5]);
  });

  it('should switch variants and update active path', () => {
    const { result } = renderHook(() => useMessageTree(mockNodes));
    
    act(() => {
      result.current.prevVariant(3); // Switch from 3 back to 2
    });
    
    // Path should now be 1 -> 2 -> 4
    expect(result.current.activePath.map(n => n.id)).toEqual([1, 2, 4]);
    
    act(() => {
      result.current.nextVariant(2); // Switch back to 3
    });
    
    expect(result.current.activePath.map(n => n.id)).toEqual([1, 3, 5]);
  });

  it('should return siblings correctly', () => {
    const { result } = renderHook(() => useMessageTree(mockNodes));
    
    const siblings = result.current.getSiblings(2);
    expect(siblings.map(n => n.id)).toEqual([2, 3]);
  });
});

import { renderHook, act } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { useMessageTree, type MessageNode } from '../useMessageTree';

const nodes: MessageNode[] = [
  { id: 1, parent_id: null, role: 'user', content: 'a', variant_index: 0 },
  { id: 2, parent_id: 1, role: 'assistant', content: 'b1', variant_index: 0 },
  { id: 3, parent_id: 1, role: 'assistant', content: 'b2', variant_index: 1 },
  { id: 4, parent_id: 3, role: 'user', content: 'c', variant_index: 0 },
  // a node with an undefined parent_id -> treated as a root (childrenMap branch)
  { id: 5, parent_id: undefined as unknown as null, role: 'user', content: 'root2', variant_index: 2 },
];

describe('useMessageTree', () => {
  it('walks the active path preferring the latest variant', () => {
    const { result } = renderHook(() => useMessageTree(nodes));
    // default active child under parent 1 is the highest variant_index (node 3),
    // then its child node 4. Root defaults to the last root (node 5).
    expect(result.current.activePath.map((n) => n.id)).toEqual([5]);
  });

  it('navigates variants with prev/next and setVariant', () => {
    const { result } = renderHook(() => useMessageTree(nodes));
    expect(result.current.getSiblings(2).map((n) => n.id)).toEqual([2, 3]);

    act(() => result.current.setVariant(null, 1)); // pick node 1 as the root
    expect(result.current.activePath.map((n) => n.id)).toEqual([1, 3, 4]);

    act(() => result.current.prevVariant(3)); // 3 -> 2
    expect(result.current.activePath.map((n) => n.id)).toEqual([1, 2]);

    act(() => result.current.nextVariant(2)); // 2 -> 3
    expect(result.current.activePath.map((n) => n.id)).toEqual([1, 3, 4]);
  });

  it('is a no-op for unknown node ids and at boundaries', () => {
    const { result } = renderHook(() => useMessageTree(nodes));
    expect(result.current.getSiblings(999)).toEqual([]);
    act(() => result.current.nextVariant(999)); // unknown -> return
    act(() => result.current.prevVariant(999)); // unknown -> return

    act(() => result.current.setVariant(null, 1));
    act(() => result.current.prevVariant(2)); // 2 is first sibling -> no change
    expect(result.current.activePath.map((n) => n.id)).toEqual([1, 3, 4]);
    act(() => result.current.nextVariant(3)); // 3 is last sibling -> no change
    expect(result.current.activePath.map((n) => n.id)).toEqual([1, 3, 4]);
  });
});

import { useState, useMemo, useCallback } from 'react';

export interface MessageNode {
  id: number;
  parent_id: number | null;
  role: 'user' | 'assistant';
  content: string;
  variant_index: number;
  timestamp?: string | Date;
}

export function useMessageTree(nodes: MessageNode[]) {
  // Map of parentId -> children nodes
  const childrenMap = useMemo(() => {
    const map = new Map<number | null, MessageNode[]>();
    nodes.forEach((node) => {
      const parentId = node.parent_id;
      if (!map.has(parentId)) {
        map.set(parentId, []);
      }
      map.get(parentId)!.push(node);
    });
    // Sort children by variant_index
    map.forEach((children) => {
      children.sort((a, b) => a.variant_index - b.variant_index);
    });
    return map;
  }, [nodes]);

  // We need to keep track of which variant is selected for each parent
  // Map of parentId -> selectedNodeId
  const [selectedVariants, setSelectedVariants] = useState<Map<number | null, number>>(new Map());

  // Function to get the active child of a parent
  const getActiveChild = useCallback((parentId: number | null): MessageNode | undefined => {
    const children = childrenMap.get(parentId);
    if (!children || children.length === 0) return undefined;

    const selectedId = selectedVariants.get(parentId);
    if (selectedId !== undefined) {
      const selectedNode = children.find(c => c.id === selectedId);
      if (selectedNode) return selectedNode;
    }

    // Default to the first child (or maybe the one with highest variant_index? 
    // Usually we want the latest one, but variant_index 0 is the first one).
    // Let's default to the one with the highest variant_index to show the latest regeneration by default.
    return children[children.length - 1];
  }, [childrenMap, selectedVariants]);

  // Compute the active path from the root
  const activePath = useMemo(() => {
    const path: MessageNode[] = [];
    let currentParentId: number | null = null;

    while (true) {
      const child = getActiveChild(currentParentId);
      if (!child) break;
      path.push(child);
      currentParentId = child.id;
    }

    return path;
  }, [getActiveChild]);

  const setVariant = useCallback((parentId: number | null, nodeId: number) => {
    setSelectedVariants(prev => {
      const next = new Map(prev);
      next.set(parentId, nodeId);
      return next;
    });
  }, []);

  const nextVariant = useCallback((nodeId: number) => {
    const node = nodes.find(n => n.id === nodeId);
    if (!node) return;

    const siblings = childrenMap.get(node.parent_id) || [];
    const currentIndex = siblings.findIndex(s => s.id === nodeId);
    if (currentIndex < siblings.length - 1) {
      setVariant(node.parent_id, siblings[currentIndex + 1].id);
    }
  }, [nodes, childrenMap, setVariant]);

  const prevVariant = useCallback((nodeId: number) => {
    const node = nodes.find(n => n.id === nodeId);
    if (!node) return;

    const siblings = childrenMap.get(node.parent_id) || [];
    const currentIndex = siblings.findIndex(s => s.id === nodeId);
    if (currentIndex > 0) {
      setVariant(node.parent_id, siblings[currentIndex - 1].id);
    }
  }, [nodes, childrenMap, setVariant]);

  const getSiblings = useCallback((nodeId: number) => {
    const node = nodes.find(n => n.id === nodeId);
    if (!node) return [];
    return childrenMap.get(node.parent_id) || [];
  }, [nodes, childrenMap]);

  return {
    activePath,
    nextVariant,
    prevVariant,
    getSiblings,
    setVariant,
  };
}

# Frontend Message Renderer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a `MessageRenderer` component to display structured AI message sequences with roleplay-specific styling.

**Architecture:** A standalone component that accepts a sequence of blocks (thought, action, speech) or falls back to traditional message fields.

**Tech Stack:** React, TypeScript, TailwindCSS.

---

### Task 1: Create the MessageRenderer Component

**Files:**
- Create: `frontend/src/components/MessageRenderer.tsx`

- [ ] **Step 1: Write the component with Tailwind styling**

```tsx
import React from 'react';

export interface SequenceBlock {
  type: 'thought' | 'action' | 'speech';
  content: string;
}

interface MessageRendererProps {
  sequence?: SequenceBlock[];
  fallback?: {
    content: string;
    thought?: string;
    actions?: string[];
  };
}

const MessageRenderer: React.FC<MessageRendererProps> = ({ sequence, fallback }) => {
  if (sequence && sequence.length > 0) {
    return (
      <div className="message-container leading-relaxed">
        {sequence.map((block, i) => (
          <span 
            key={i} 
            className={
              block.type === 'thought' ? 'italic text-zinc-400 text-[0.95em]' : 
              block.type === 'action' ? 'font-bold text-zinc-300' : 
              'text-zinc-100'
            }
          >
            {block.content}
            {" "}
          </span>
        ))}
      </div>
    );
  }

  // Fallback for non-sequence messages
  return (
    <div className="flex flex-col gap-1.5">
      {fallback?.actions && fallback.actions.length > 0 && (
        <div className="px-2 text-xs font-bold text-emerald-500/80 uppercase tracking-widest">
          {fallback.actions.map(a => `**${a}**`).join(' ')}
        </div>
      )}
      <div className="p-4 rounded-2xl shadow-lg border bg-zinc-900 border-zinc-800 text-zinc-100 rounded-tl-none">
        {fallback?.thought && (
          <div className="text-sm italic text-zinc-400 mb-2 border-l-2 border-emerald-500/30 pl-3 py-0.5">
            {fallback.thought}
          </div>
        )}
        <p className="whitespace-pre-wrap leading-relaxed">
          {fallback?.content}
        </p>
      </div>
    </div>
  );
};

export default MessageRenderer;
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/MessageRenderer.tsx
git commit -m "feat(frontend): add MessageRenderer component for structured sequences"
```

### Task 2: Integrate into App.tsx

**Files:**
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: Update Message interface and import renderer**

Add `sequence` to `Message` interface and import `MessageRenderer`.

- [ ] **Step 2: Update message rendering loop**

Replace the current manual message rendering logic with `<MessageRenderer />`.

- [ ] **Step 3: Update handleSend to capture sequence from API**

Update the API response parsing to include `data.sequence`.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/App.tsx
git commit -m "feat(frontend): integrate MessageRenderer into App"
```

### Task 3: Verification

- [ ] **Step 1: Mock a sequence message in state**

Temporarily add a mock message to the `messages` state in `App.tsx` to verify styling.

- [ ] **Step 2: Verify visual styling**

Check if thought is italic/gray, action is bold, and speech is standard.

- [ ] **Step 3: Verify fallback**

Ensure user messages and old-style assistant messages still render correctly.

- [ ] **Step 4: Cleanup mock data and final commit**

```bash
git add frontend/src/App.tsx
git commit -m "test(frontend): verify MessageRenderer visual styling and fallback"
```

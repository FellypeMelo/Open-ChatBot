# Character-Immersive Rebase Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform Open-ChatBot into a high-performance, immersive narrative engine with a deep structural rebase, branching history (Message Tree), and optimized Python orchestration.

**Architecture:** 
1.  **Structural Rebase:** Move existing Python/React files into a clean `src/backend` and `src/frontend` hierarchy.
2.  **Message Tree:** Implement a Directed Acyclic Graph (DAG) for chat history to support "Swiping" for alternative responses.
3.  **Cinematic HUD:** Implement 60FPS smoothed token streaming and distinct block rendering (Thoughts/Actions/Speech).
4.  **Lorebooks:** Integrate keyword-triggered vector retrieval (via chromadb) into the prompt pipeline.

**Tech Stack:** Python (FastAPI), React (TypeScript), SQLite, llama.cpp.

---

### Phase 1: Rebase & Structural Cleanup

#### Task 1: Reorganize Backend Structure
**DONE**

#### Task 2: Reorganize Frontend Structure
**DONE**

---

### Phase 2: Message Tree (Branching History)

#### Task 3: Database Schema Migration
**DONE**

#### Task 4: Frontend "Swipe" Navigation
**DONE**

---

### Phase 3: Cinematic HUD & 60FPS Streaming

#### Task 5: Implement Token Queue (Frontend)
**Files:**
- Create: `src/frontend/src/hooks/useTokenQueue.ts`
- Modify: `src/frontend/src/components/ChatView.tsx`

- [ ] **Step 1: Implement smoothing buffer**
A hook that receives tokens from the WebSocket/SSE and pushes them to a local display buffer at a fixed interval (e.g., 16ms for 60fps).

- [ ] **Step 2: Verify fluid text appearance**
Test with high-latency inference to ensure no "stuttering".

- [ ] **Step 3: Commit**
```bash
git add src/frontend
git commit -m "feat: 60fps token streaming"
```

#### Task 6: Narrative Block Renderer
**Files:**
- Modify: `src/frontend/src/components/MessageRenderer.tsx`

- [ ] **Step 1: Update renderer for Thoughts/Actions/Speech**
Apply the Obsidian Narrative design (italics, dimmed zinc for thoughts; bold for actions).

- [ ] **Step 2: Final E2E Validation**
Verify that a swiped message correctly renders with smoothed streaming and immersive styling.

- [ ] **Step 3: Commit**
```bash
git commit -m "feat: immersive narrative rendering"
```

---

### Phase 4: Lorebooks & Context Fusion

#### Task 7: Integrate Lorebook Retrieval
**Files:**
- Modify: `src/backend/core/orchestration/bridge.py`
- Test: `src/backend/__tests__/test_lorebooks.py`

- [ ] **Step 1: Implement keyword extraction and retrieval logic**
Update the `Brain.build_prompt` to extract keywords from user input and query `VectorStore`.

- [ ] **Step 2: Write tests for lore injection**

- [ ] **Step 3: Final Commit**
```bash
git commit -m "feat: complete immersive rebase with lorebooks"
```

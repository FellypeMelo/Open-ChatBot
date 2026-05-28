# Evolution & Immersion System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a dynamic character evolution engine and a cinematic narrative HUD to maximize immersion.

**Architecture:** 
1.  **Backend Evolution**: Tiered relationship logic and state-driven prompt modifiers.
2.  **Frontend Atmosphere**: Dynamic background blur, 60FPS-synced typewriter audio, and immersive vignette overlays.
3.  **Autonomous State**: Action-parsing logic that allows AI to self-update its clothes/location.

**Tech Stack:** Python (FastAPI), React (TypeScript), Lucide Icons, Howler.js (Audio).

---

### Phase 1: Character Evolution (Logic)

#### Task 1: Relationship Tiers & Dynamic Prompts
**Files:**
- Create: `src/backend/core/orchestration/evolution.py`
- Modify: `src/backend/core/orchestration/bridge.py`
- Test: `src/backend/__tests__/test_evolution.py`

- [ ] **Step 1: Implement tier logic in evolution.py**
```python
def get_tier_instructions(score: int) -> str:
    if score >= 80: return "You are deeply intimate with the user."
    if score >= 50: return "You are warm and friendly."
    return "You are professional and distant."
```

- [ ] **Step 2: Integrate into Brain.build_prompt**
Call `get_tier_instructions` and inject into a new `# SOCIAL DYNAMICS #` section.

- [ ] **Step 3: Commit**
```bash
git add src/backend/core/orchestration/ src/backend/__tests__/
git commit -m "feat(backend): tiered relationship logic"
```

#### Task 2: State-Driven Narrative Interrupts
**Files:**
- Modify: `src/backend/core/orchestration/evolution.py`

- [ ] **Step 1: Implement get_forced_modifiers(stats)**
Logic to return "EXHAUSTED" or "STARVING" modifiers that override character personality.

- [ ] **Step 2: Commit**

---

### Phase 2: Cinematic HUD (Senses)

#### Task 3: Dynamic Atmosphere Hook
**Files:**
- Create: `src/frontend/src/hooks/useAtmosphere.ts`
- Modify: `src/frontend/src/components/ChatView.tsx`

- [ ] **Step 1: Implement useAtmosphere**
Hook that tracks "currentBlockType" and returns `blurAmount` and `textOpacity`.

- [ ] **Step 2: Integrate Blur into ChatView**
Apply `backdrop-filter: blur(Npx)` to the character background based on the hook.

- [ ] **Step 3: Commit**

#### Task 4: Token-Synced Audio (Typewriter)
**Files:**
- Create: `src/frontend/src/hooks/useAudio.ts`
- Modify: `src/frontend/src/hooks/useTokenQueue.ts`

- [ ] **Step 1: Implement sound triggers**
Play randomized soft clicks on every token release in `useTokenQueue`.

- [ ] **Step 2: Commit**

---

### Phase 3: Autonomous State (Action Parsing)

#### Task 5: Narrative Action Parser
**Files:**
- Modify: `src/backend/api/chat.py`

- [ ] **Step 1: Implement parse_actions_to_state(ai_response)**
Regex to detect `**enters [location]**` or `**changes into [outfit]**`.

- [ ] **Step 2: Update AgentState in DB**
Update `location` or `clothes` if detected.

- [ ] **Step 3: Commit**

#### Task 4: Final Verification
- [ ] **Step 1: E2E Test**
Send "Go to the library" -> AI responds "**Gemi enters the library.**" -> HUD status bar should update to "Location: Library".

- [ ] **Step 2: Final Commit**
```bash
git commit -m "feat: complete evolution and immersion system"
```

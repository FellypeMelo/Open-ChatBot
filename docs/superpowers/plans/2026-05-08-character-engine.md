# High-Fidelity Character Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform Open-ChatBot into a JanitorAI-style immersive roleplay engine with persistent user identity, sequence-based narrative JSON, and reactive gameplay mechanics.

**Architecture:** 
1.  **User Persistence:** Add a `User` table to the database.
2.  **Sequence Parsing:** Switch `LlamaClient` and `Brain` to return an ordered `sequence` of typed blocks (thought, action, speech).
3.  **Stat-Driven Behavior:** Injected prompt modifiers based on Energy, Hunger, and Relationship levels.
4.  **Immersive UI:** A sequence renderer in the frontend with specific styling for each block type.

**Tech Stack:** FastAPI, SQLAlchemy, React (TypeScript), CSS Modules.

---

### Task 1: Database - User Model & Character Enhancements

**Files:**
- Modify: `app/db/models.py`
- Modify: `app/db/database.py` (ensure creation)

- [ ] **Step 1: Add User model and Character fields**

```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    gender = Column(String)
    is_active = Column(Boolean, default=True)

# Update Character
class Character(Base):
    # ... existing fields ...
    short_description = Column(Text)
```

- [ ] **Step 2: Update database initialization**
- [ ] **Step 3: Verify with test script**
- [ ] **Step 4: Commit**

### Task 2: Core - State-to-Behavior Mapping

**Files:**
- Create: `app/core/evolution.py` (or update if exists)
- Test: `tests/test_evolution.py`

- [ ] **Step 1: Implement the behavioral mapper**

```python
def get_behavioral_modifiers(stats: dict) -> str:
    mods = []
    energy = stats.get("energy", 100)
    if energy < 20:
        mods.append("EXHAUSTED: You are barely able to speak. Short sentences, slurred words.")
    # ... other stats ...
    return "\n".join(mods)
```

- [ ] **Step 2: Write tests for mapping levels**
- [ ] **Step 3: Commit**

### Task 3: API & LLM - Sequence-Based JSON

**Files:**
- Modify: `app/api/chat.py`
- Modify: `app/core/bridge.py`

- [ ] **Step 1: Update GBNF Grammar for sequences**

```python
SEQUENCE_GRAMMAR = r'''
root ::= "{" space "\"sequence\"" ":" space "[" space (block ("," space block)*)? space "]" space "}"
block ::= "{" space type_field "," space content_field space "}"
type_field ::= "\"type\"" ":" space ("\"thought\"" | "\"action\"" | "\"speech\"")
content_field ::= "\"content\"" ":" space string
'''
```

- [ ] **Step 2: Update Prompt Construction to include User info**
- [ ] **Step 3: Commit**

### Task 4: Frontend - Sequence Message Component

**Files:**
- Create: `frontend/src/components/MessageRenderer.tsx`
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: Create the renderer component**

```tsx
const MessageRenderer = ({ sequence }) => (
  <div>
    {sequence.map((block, i) => (
      <p key={i} className={`block-${block.type}`}>
        {block.type === 'thought' ? <i>{block.content}</i> : block.content}
      </p>
    ))}
  </div>
);
```

- [ ] **Step 2: Apply CSS for JanitorAI styling (gray thoughts, bold actions)**
- [ ] **Step 3: Commit**

### Task 5: Final - User Profile Settings UI

- [ ] **Step 1: Add simple form to set Name/Gender**
- [ ] **Step 2: Connect frontend state to API**
- [ ] **Step 3: Final E2E Verification**
- [ ] **Step 4: Commit**

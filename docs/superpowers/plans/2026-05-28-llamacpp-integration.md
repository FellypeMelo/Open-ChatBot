# llama.cpp Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enable dynamic llama.cpp server configuration from the frontend.

**Architecture:** Frontend stores settings in `localStorage`, sends them with chat requests, and the Backend uses them to override default connection settings.

**Tech Stack:** FastAPI, Pydantic, React (TS), httpx.

---

### Task 1: Update Backend API Schema

**Files:**
- Modify: `src/backend/api/chat.py`

- [ ] **Step 1: Add LLMConfig schema and update ChatRequest**

```python
class LLMConfig(BaseModel):
    base_url: Optional[str] = None
    model_name: Optional[str] = None

class ChatRequest(BaseModel):
    message: Optional[str] = None
    character_id: int = 1
    parent_id: Optional[int] = None
    config: Optional[LLMConfig] = None # New field
```

- [ ] **Step 2: Verify with manual check of the file content**

---

### Task 2: Refactor LlamaClient for Dynamic Context

**Files:**
- Modify: `src/backend/core/engine/llm.py`

- [ ] **Step 1: Update method signatures to accept dynamic config**

Modify `complete`, `complete_stream`, and `embed` to take optional overrides.

```python
    async def complete(self, prompt: str, grammar: str = None, url: str = None, model: str = None):
        target_url = url or self.url
        # ... use target_url ...
        if model:
            payload["model"] = model # Add model name if provided
```

- [ ] **Step 2: Update complete_stream similarly**

---

### Task 3: Update Chat Endpoints to Use Dynamic Config

**Files:**
- Modify: `src/backend/api/chat.py`

- [ ] **Step 1: Extract config in `chat` and `chat_stream`**

```python
@router.post("/chat")
async def chat(request: ChatRequest, ...):
    config = request.config or LLMConfig()
    # ...
    result = await llama.complete(prompt, url=config.base_url, model=config.model_name)
```

- [ ] **Step 2: Repeat for `chat_stream`**

---

### Task 4: Frontend Settings Persistence

**Files:**
- Create: `src/frontend/src/hooks/useSettings.ts`

- [x] **Step 1: Implement localStorage hook for LLM config**

```typescript
import { useState, useEffect } from 'react';

export interface LLMConfig {
  base_url: string;
  model_name: string;
}

export const useSettings = () => {
  const [config, setConfig] = useState<LLMConfig>(() => {
    const saved = localStorage.getItem('llm_config');
    return saved ? JSON.parse(saved) : { base_url: 'http://localhost:8080', model_name: '' };
  });

  useEffect(() => {
    localStorage.setItem('llm_config', JSON.stringify(config));
  }, [config]);

  return { config, setConfig };
};
```

---

### Task 5: Update Frontend API Service

**Files:**
- Modify: `src/frontend/src/services/api.ts`

- [ ] **Step 1: Update chat and chatStream functions**

```typescript
export interface LLMConfig {
  base_url?: string;
  model_name?: string;
}

export const sendMessage = async (message: string, characterId: number, parentId: number | null, config?: LLMConfig) => {
  const response = await fetch('/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, character_id: characterId, parent_id: parentId, config })
  });
  // ...
};
```

---

### Task 6: Implement Settings UI

**Files:**
- Create: `src/frontend/src/components/SettingsModal.tsx`
- Modify: `src/frontend/src/components/Sidebar.tsx`

- [ ] **Step 1: Create SettingsModal with input fields for URL and Model**
- [ ] **Step 2: Add "Settings" button to Sidebar to open the modal**

---

### Task 7: Validation

- [ ] **Step 1: Run backend tests to ensure no regressions**
- [ ] **Step 2: Manually verify that changing the model name in the UI reaches the backend (check logs)**

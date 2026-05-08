# Pre-Test Analysis Audit Report

Date: 2026-05-08

## 1. Backend Issues

### 1.1 Strict JSON Parsing Risks
- **Issue:** The `ACTION_GRAMMAR` enforces a very specific structure. LLMs often add markdown, comments, or extra text.
- **Risk:** High chance of `JSONDecodeError` even with regex fallback if the LLM output is severely malformed.
- **Resolution:** Improve the regex fallback to be more robust (already partially done) and consider "loose" parsing.

### 1.2 Database Schema / State Corruption
- **Issue:** `agent_states.stats` is a JSON field with no schema enforcement at the DB level.
- **Risk:** If a key is missing (e.g., `relationship`), logic in `evolution.py` or `world.py` might fail.
- **Resolution:** Add a "migration" or "sync" step that ensures all expected keys exist with default values whenever stats are loaded.

### 1.3 Missing Concurrency Handling
- **Issue:** Background tasks in `chat.py` modify the database. If a user sends messages very rapidly, there might be race conditions on the character state.
- **Risk:** Corrupted or lost character growth data.
- **Resolution:** Consider adding a locking mechanism or serializing evolution tasks for a specific character.

## 2. Frontend Issues

### 2.1 State Desynchronization
- **Issue:** The HUD bars depend on the `stats` object returned in the chat response. If the AI fails to generate valid JSON, the response returns the current state, but if that's also empty, the HUD might break.
- **Risk:** UI flickering or empty progress bars.
- **Resolution:** Ensure the `stats` field is always populated in `ChatResponse`, even on error.

### 2.2 Memory Rendering
- **Issue:** The sequence renderer expects specific types (`thought`, `action`, `speech`). If the AI hallucinating new types, they won't be rendered.
- **Risk:** Lost information in the chat.
- **Resolution:** Add a default case to `MessageRenderer.tsx` to render unknown types as standard text.

## 3. Reliability & Edge Cases

### 3.1 LLM Timeouts
- **Issue:** `LlamaClient` has a 60s timeout. Complex reflections or long prompts might hit this.
- **Risk:** 500 error on the frontend.
- **Resolution:** Implement retries or better timeout handling.

### 3.2 Vector Store Cleanup
- **Issue:** Tests might leave data in `chroma_db`.
- **Risk:** Flaky tests or contamination.
- **Resolution:** Ensure tests use a temporary directory for ChromaDB or mock the `VectorStore`.

---

## Next Steps:
1. Implement "Safe Stat Loading" in `app/api/chat.py`.
2. Update `MessageRenderer.tsx` with a default type case.
3. Add a more robust JSON cleaner in `app/api/chat.py`.
4. Proceed to Phase 2: Deep E2E Testing.

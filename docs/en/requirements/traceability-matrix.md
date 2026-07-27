# Requirements Traceability Matrix (RTM)

This matrix tracks the relationship between engineering requirements, business rules, and their actual implementation in the codebase.

> **Note on currency:** this matrix was written against an earlier snapshot of the codebase. Two implementation pointers below (`evolution.py`) named a module that no longer exists — that logic now lives in `core/engine/state_transitions.py` and `core/engine/engine.py`, and the two rows have been updated to point there. Line-number anchors have been dropped throughout (they drift as the code changes and could not be re-verified line-by-line for this pass); treat the file links as pointers to the right module, not a guarantee of the exact line.

## 1. Functional Requirements (RF)

| Requirement ID | Description | Component / Module | Implementation Code / File | Status |
| :--- | :--- | :--- | :--- | :--- |
| **RF-001** | Character Persistence | Database schemas & Character API | [models.py](../../../src/backend/db/models.py) (`Character`), [characters.py](../../../src/backend/api/characters.py) (CRUD routes) | **Implemented** |
| **RF-002** | Dynamic Tag System | DB Tag entities & Prompt generation | [models.py](../../../src/backend/db/models.py) (`Tag`), [bridge.py](../../../src/backend/core/orchestration/bridge.py) (`build_prompt` layer) | **Implemented** |
| **RF-003** | Narrative Sequence Rendering | Sequence Parser & HTML rendering | [validator.py](../../../src/backend/core/orchestration/validator.py), Frontend ChatView parser (CSS formatting of Thoughts/Actions) | **Implemented** |
| **RF-004** | State-to-Behavior Mapping | Bio-state updater & Dynamic Prompt Modifiers | [state_transitions.py](../../../src/backend/core/engine/state_transitions.py) (`parse_actions_to_state`, `apply_action_stats`), [bridge.py](../../../src/backend/core/orchestration/bridge.py) (`build_prompt` state layer) | **Implemented** |
| **RF-005** | User Profile Management | User database persistence & prompt interpolation | [models.py](../../../src/backend/db/models.py) (`User`), [users.py](../../../src/backend/api/users.py) (routes), [bridge.py](../../../src/backend/core/orchestration/bridge.py) | **Implemented** |
| **RF-006** | Vector-Based Long-Term Memory | Local TurboQuant Vector database | [vector_store.py](../../../src/backend/core/memory/vector_store.py) (`VectorStore`), [bridge.py](../../../src/backend/core/orchestration/bridge.py) (memory/RAG layer) | **Implemented** |

## 2. Business Rules (RN)

| Rule ID | Rule Statement | Implementation File / Code | Status |
| :--- | :--- | :--- | :--- |
| **RN-001** | Personality Priority | [bridge.py](../../../src/backend/core/orchestration/bridge.py) (`build_prompt` loads `character.description` directly as the Identity layer, which overrides global base guidelines inside template orchestration) | **Implemented** |
| **RN-002** | State-Behavior Thresholds | [state_transitions.py](../../../src/backend/core/engine/state_transitions.py) (stat-delta thresholds for the low-energy/high-hunger/high-relationship narrative modifiers) | **Implemented** |
| **RN-003** | Formatting Enforced | [validator.py](../../../src/backend/core/orchestration/validator.py) (requires >= 1 thought `*...*` and >= 1 action `**...**` if word count > 50 words) | **Implemented** |
| **RN-004** | Memory Retention & Summary | [bridge.py](../../../src/backend/core/orchestration/bridge.py) (`reflect` method parses user facts and summary on the reflection interval, resetting local chat history bloat) | **Implemented** |
| **RN-005** | Audit Trail | [chat.py](../../../src/backend/api/chat.py) (`request_id` generated via UUID, logged with every inference stream, and saved in the `MessageNode` schema) | **Implemented** |

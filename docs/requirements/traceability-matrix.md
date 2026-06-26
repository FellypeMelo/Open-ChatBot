# Requirements Traceability Matrix (RTM)

This matrix tracks the relationship between engineering requirements, business rules, and their actual implementation in the codebase.

## 1. Functional Requirements (RF)

| Requirement ID | Description | Component / Module | Implementation Code / File | Status |
| :--- | :--- | :--- | :--- | :--- |
| **RF-001** | Character Persistence | Database schemas & Character API | [models.py](file:///G:/Programas/Open-ChatBot/src/backend/db/models.py#L27-L43) (`Character`), [characters.py](file:///G:/Programas/Open-ChatBot/src/backend/api/characters.py) (CRUD routes) | **Implemented** |
| **RF-002** | Dynamic Tag System | DB Tag entities & Prompt generation | [models.py](file:///G:/Programas/Open-ChatBot/src/backend/db/models.py#L14-L19) (`Tag`), [bridge.py](file:///G:/Programas/Open-ChatBot/src/backend/core/orchestration/bridge.py#L112-L117) (`build_prompt` Layer 3) | **Implemented** |
| **RF-003** | Narrative Sequence Rendering | Sequence Parser & HTML rendering | [validator.py](file:///G:/Programas/Open-ChatBot/src/backend/core/orchestration/validator.py#L6-L30) (`validate_narrative_formatting`), Frontend ChatView parser (CSS formatting of Thoughts/Actions) | **Implemented** |
| **RF-004** | State-to-Behavior Mapping | Bio-state updater & Dynamic Prompt Modifiers | [evolution.py](file:///G:/Programas/Open-ChatBot/src/backend/core/orchestration/evolution.py#L44-L74) (`get_forced_modifiers`), [bridge.py](file:///G:/Programas/Open-ChatBot/src/backend/core/orchestration/bridge.py#L118-L133) (`build_prompt` Layer 4) | **Implemented** |
| **RF-005** | User Profile Management | User database persistence & prompt interpolation | [models.py](file:///G:/Programas/Open-ChatBot/src/backend/db/models.py#L20-L25) (`User`), [users.py](file:///G:/Programas/Open-ChatBot/src/backend/api/users.py) (routes), [bridge.py](file:///G:/Programas/Open-ChatBot/src/backend/core/orchestration/bridge.py#L134) (Layer 4) | **Implemented** |
| **RF-006** | Vector-Based Long-Term Memory | Local TurboQuant Vector database | [vector_store.py](file:///G:/Programas/Open-ChatBot/src/backend/core/memory/vector_store.py#L66-L153) (`VectorStore`), [bridge.py](file:///G:/Programas/Open-ChatBot/src/backend/core/orchestration/bridge.py#L86-L92) (Layer 1) | **Implemented** |

## 2. Business Rules (RN)

| Rule ID | Rule Statement | Implementation File / Code | Status |
| :--- | :--- | :--- | :--- |
| **RN-001** | Personality Priority | [bridge.py](file:///G:/Programas/Open-ChatBot/src/backend/core/orchestration/bridge.py#L113) (`build_prompt` loads `character.description` directly as Identity layer which overrides global base guidelines inside template orchestration) | **Implemented** |
| **RN-002** | State-Behavior Thresholds | [evolution.py](file:///G:/Programas/Open-ChatBot/src/backend/core/orchestration/evolution.py#L44-L74) (Defines thresholds: Energy $\le$ 30% / $\le$ 10%, Hunger $\ge$ 70% / $\ge$ 90%, Happiness < 20%) | **Implemented** |
| **RN-003** | Formatting Enforced | [validator.py](file:///G:/Programas/Open-ChatBot/src/backend/core/orchestration/validator.py#L6-L30) (Requires $\ge$ 1 thought `*...*` and $\ge$ 1 action `**...**` if word count > 50 words) | **Implemented** |
| **RN-004** | Memory Retention & Summary | [bridge.py](file:///G:/Programas/Open-ChatBot/src/backend/core/orchestration/bridge.py#L157-L173) (`reflect` method parses user facts and summary every 20 interaction counts, resetting local chat history bloat) | **Implemented** |
| **RN-005** | Audit Trail | [chat.py](file:///G:/Programas/Open-ChatBot/src/backend/api/chat.py#L234) (`request_id` generated via UUID, logged with every inference stream, and saved in `MessageNode` schema) | **Implemented** |

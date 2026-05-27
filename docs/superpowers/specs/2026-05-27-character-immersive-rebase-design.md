# Design Spec: High-Immersion Narrative Engine Rebase (vNext)

## 1. Overview
This project transforms the existing Open-ChatBot into a high-performance, immersive narrative engine inspired by Character.ai and Janitor.ai. The rework involves a deep structural rebase, a transition to a branching message tree architecture, and optimized Python orchestration for critical-path operations.

## 2. Goals
*   **Architectural Purity**: Clean, modular directory structure following enterprise standards.
*   **Narrative Branching**: Support for "Swiping" (multiple response variants) via a Radix Tree history.
*   **Performance**: Optimized prompt assembly and near-zero prefill via `llama.cpp` server-side caching.
*   **Cinematic Immersion**: 60FPS smoothed token streaming and distinct narrative block rendering (Thoughts, Actions, Speech).

## 3. Revised Directory Structure
The project will be reorganized into the following structure:

```text
G:\Programas\Open-ChatBot\
├───docs\                       # Project documentation (ADRs, Specs)
├───infra\                      # llama.cpp binaries and deployment scripts
├───src\
│   ├───backend\
│   │   ├───api\                # FastAPI routes (chat, characters, tags, users)
│   │   ├───core\
│   │   │   ├───orchestration\  # Prompt stitching, Lorebooks, State Mapping
│   │   │   ├───engine\         # llama.cpp lifecycle and streaming bridge
│   │   │   └───memory\         # Message Tree logic and Radix history
│   │   ├───db\                 # SQLAlchemy models and migrations
│   │   └───__tests__\          # Isolated unit and integration tests
│   └───frontend\
│       ├───src\
│       │   ├───components\     # UI components (HUD, Renderer, Sidebars)
│       │   ├───services\       # API client and Streaming handlers
│       │   ├───hooks\          # HUD State, Narrative Flow hooks
│       │   └───store\          # Global state management
│       └───... (Vite config)
├───shared\                     # Pydantic/TS models shared across tiers
└───scripts\                    # Maintenance and reset utilities
```

## 4. Key Systems Design

### 4.1. The Message Tree (Branching History)
Instead of a linear list, chat history will be stored as a **Directed Acyclic Graph (DAG)** or **Radix Tree**.
*   **Model**: `MessageNode` { id, parent_id, role, content, type (thought/action/speech), variant_index }.
*   **Logic**: Users can "swipe" to generate a new sibling node. The UI tracks the `active_path` (a list of node IDs) to render the current branch.
*   **Persistence**: SQLite remains the SSoT, with nodes indexed by `character_id` and `user_id`.

### 4.2. Optimized Python Orchestration
*   **JSON**: Use `orjson` for ultra-fast serialization in the FastAPI layer.
*   **Vector Search**: Leverage `chromadb` (using its C++ backed bindings) for Lorebook retrieval, ensuring searches happen in milliseconds without custom native modules.
*   **Prefix Caching**: Utilize `llama.cpp`'s HTTP server parameters (`--slot-save-path`) to maintain KV-caches for branched paths, reducing prefill time.

### 4.3. Lorebooks & Dynamic Context Fusion
*   **Lorebooks**: Global and character-specific entries triggered by keywords.
*   **Fusion**: The `Orchestrator` will:
    1.  Extract keywords from the user's message.
    2.  Query the `VectorStore` for relevant lore.
    3.  Stitch the lore, character prompt, state-modifiers (Energy/Hunger), and the active history path into a final optimized prompt.

### 4.4. Cinematic HUD & Rendering
*   **60FPS Token Queue**: A frontend buffer that collects incoming tokens from the stream and releases them at a constant, configurable rate to mimic human typing without jitter.
*   **Narrative Renderer**: 
    *   `thought`: *Italic, dimmed zinc.*
    *   `action`: **Bold, narrative-weight white.**
    *   `speech`: Clear, legible dialogue bubbles or centered text.

## 5. Implementation Strategy
1.  **Phase 1: Rebase**: Move existing Python files into the new `src/backend` and `src/frontend` structure. Update imports.
2.  **Phase 2: Tree Engine**: Implement the `MessageNode` schema and the "Active Path" logic in the backend and frontend.
3.  **Phase 3: Cinematic HUD**: Refactor the frontend to support smoothed streaming and the narrative console aesthetic.
4.  **Phase 4: Lorebooks**: Integrate keyword-triggered retrieval into the prompt pipeline.

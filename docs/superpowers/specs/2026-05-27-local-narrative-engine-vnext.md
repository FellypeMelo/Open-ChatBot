# Design Spec: High-Immersion Local Narrative Engine (vNext)

## 1. Executive Summary
Inspired by the architectures of Character.AI (vertical optimization) and Janitor AI (behavioral flexibility), this spec defines a local-first, single-user interaction engine. The goal is maximum immersion through ultra-low latency, persistent memory, and cinematic narrative formatting, running entirely on local hardware via `llama.cpp`.

## 2. Core Feature Set (Extracted from Analysis)

### 2.1. Behavioral Logic Framework (Lorebooks & Scripts)
*   **Lorebooks**: A searchable vector-based dictionary of world facts, character history, and specific triggers.
*   **Dynamic Scripts**: Conditional logic that modifies the system prompt based on user input or state (e.g., if user mentions "food", inject Hunger-specific behavioral instructions).
*   **Context Fusion**: The engine will dynamically "stitch" Lorebook snippets and Script outputs into the prompt before inference.

### 2.2. Cinematic Messaging UX
*   **60FPS Token Queue**: Frontend logic to smooth out `llama.cpp` streaming, ensuring text appears fluidly at human-reading speeds.
*   **Narrative Block Rendering**: 
    *   *Thoughts*: italicized, low-opacity.
    *   **Actions**: bold, narrative weight.
    *   Dialogue: primary text.
*   **Swipe to Regenerate**: Support for multiple response branches per turn, managed as a Radix Tree in the database.

### 2.3. Memory & State Efficiency
*   **RadixAttention (Local Equivalent)**: Leveraging `llama.cpp`'s context shifting to reuse prefix caches for the system prompt and long character descriptions, reducing "prefill" time to near-zero for the single user.
*   **Reflections**: Periodic background summarization of the last 20 messages to keep the context window focused on immediate interaction.

## 3. Technology Stack Evaluation: Python vs. Performance Mode

### 3.1. Current Choice: Python (FastAPI) + SQLite
*   **Pros**: Rapid development of complex "Prompt Stitching" logic; easy integration with `llama.cpp`'s HTTP server; single-file database portability.
*   **Cons**: Global Interpreter Lock (GIL) and slightly higher latency in the orchestration layer.

### 3.2. "Maximum Performance" Option: Rust or Go
*   **Pros**: Lower memory footprint; true parallelism for background tasks (vector searches, logging, state mapping).
*   **Recommendation**: **Stay with Python for the Orchestration Layer**, but optimize critical paths:
    *   Use `ujson` or `orjson` for high-speed JSON parsing.
    *   Offload Vector Search (Lorebooks) to a native C++/Rust library like `faiss` or `annoy` via Python bindings.
    *   Ensure the `llama.cpp` bridge uses non-blocking asynchronous I/O.

## 4. Implementation Priorities (Milestones)

1.  **Phase A (Infrastructure)**: Robust `llama.cpp` process manager and HTTP streaming bridge.
2.  **Phase B (Immersion)**: Frontend "Narrative Renderer" and state-based prompt injector.
3.  **Phase C (Complexity)**: Lorebook management and automated character "Reflections".

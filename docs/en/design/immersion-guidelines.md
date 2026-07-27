# Design Standards: Janitor AI / Character AI Immersion

## 1. Visual Aesthetics
*   **Cinematic HUD**: The interface should feel like a "Narrative Console" rather than a standard chat app.
*   **Aesthetics**: Minimalist, dark-themed by default, with high-contrast typography for legibility.
*   **Immersive Backgrounds**: Support for character-specific background images or blurred cinematic overlays.

## 2. Messaging UX
*   **Real-time Streaming**: Words should appear as they are generated, mimicking a "typing" feel.
*   **Narrative Blocks**: Distinct visual separation between:
    *   **Thoughts**: Small, italicized, slightly transparent text.
    *   **Actions**: Bold, narrative-weight text.
    *   **Speech**: Large, clear dialogue bubbles or centered text blocks.
*   **Interaction**: Hover effects on messages to show "metadata" (e.g., affection impact, energy cost).

## 3. Character Interaction Model
*   **Persona Profile**: A dedicated sidebar or expandable view showing:
    *   Dynamic Tags (current mood/behavior).
    *   Status Bars (Energy, Hunger, Relationship).
    *   "Long-term Memory" snippets currently in focus.

## 4. Single-User Flow
*   **Local Persistence**: No login required; the system loads the local user profile automatically from `chatbot.db`.
*   **Offline Mode**: Primary operation is offline via `llama.cpp`. A visual indicator shows the "Engine Status" (Model loaded, Token/sec, VRAM usage).

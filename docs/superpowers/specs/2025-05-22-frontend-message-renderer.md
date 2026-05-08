# Frontend Message Renderer Design

## Goal
Implement a structured message renderer for AI responses that supports "story-fy" JSON sequences (thought, action, speech) with JanitorAI-inspired styling.

## Architecture
- **Component-Based:** A standalone `MessageRenderer` component will handle the parsing and rendering of sequence blocks.
- **Fallback Support:** Maintain compatibility with the existing `content`, `thought`, and `actions` fields.
- **Styling:** Use TailwindCSS classes to match the existing dark, high-contrast theme.

## Components
### `MessageRenderer`
- **Props:**
  - `sequence`: `SequenceBlock[]` (optional)
  - `fallback`: `FallbackData` (required)
- **Styling Logic:**
  - `thought`: Italic, grayed out (`text-zinc-400`), slightly smaller.
  - `action`: Bold, slightly dimmed white/gray (`text-zinc-300`).
  - `speech`: Standard white (`text-zinc-100`).

## Data Flow
1. `App.tsx` receives a message from the API.
2. If `sequence` exists in the response, it's stored in the message object.
3. `MessageRenderer` receives the message data and prefers `sequence` for rendering.
4. If `sequence` is missing, it renders the message using the traditional blocks.

## Testing Strategy
- Manual verification using a mock message with a `sequence` payload in `App.tsx` initial state.
- Verify fallback behavior by sending a standard message.

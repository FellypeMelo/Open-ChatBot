# Design Spec: High-Fidelity Character Engine & User Profiles

## 1. Overview
Transform the current chatbot into a high-fidelity character interaction engine similar to JanitorAI/CharacterAI. This involves persistent user identity, deeper emotional immersion, reactive gameplay mechanics (Energy/Hunger/Relationship), and structured narrative formatting.

## 2. Goals
- **Personalization:** The AI recognizes the user's name and gender across sessions.
- **Immersion:** Characters express complex, interleaved sequences of thoughts, actions, and speech.
- **Reactivity:** Biological and social stats (Energy, Hunger, Relationship) meaningfully influence AI behavior.
- **Visual Clarity:** Frontend renders thoughts, actions, and speech with distinct styling (Italics, Bold, etc.).

## 3. Architecture & Data Model

### 3.1 Database Changes
- **New `User` Model:**
    - `id`: Integer (Primary Key)
    - `name`: String
    - `gender`: String (e.g., Male, Female, Non-binary)
    - `is_active`: Boolean (Default: True)
- **Character Model Update:**
    - Add `short_description`: Text (for UI display).
    - Enhance `description` to support complex persona blocks.

### 3.2 State-to-Behavior Mapping (Backend)
A new utility layer will translate raw `AgentState` values into descriptive prompt modifiers:
- **Energy (0-100):**
    - < 20: "Exhausted, slurred speech, short sentences."
    - 20-50: "Tired, low initiative."
- **Hunger (0-100):**
    - > 80: "Starving, irritable, distracted by food."
- **Relationship (0-100):**
    - Tiers: Stranger (0-20), Acquaintance (21-50), Friend (51-80), Close (81-100).

## 4. Interaction Logic

### 4.1 "Sequence of Blocks" JSON Format
The AI will switch from fixed fields to a chronological sequence of narrative blocks:
```json
{
  "sequence": [
    {"type": "thought", "content": "I wonder if they noticed..."},
    {"type": "action", "content": "She tucks a strand of hair behind her ear."},
    {"type": "speech", "content": "Do you like it?"},
    {"type": "action", "content": "She waits for a response with a hopeful smile."}
  ]
}
```

### 4.2 Enhanced Prompting Strategy
The `MASTER_PROMPT` will be updated to enforce:
- **Narrative Continuity:** Referencing previous emotional states and user interactions.
- **Character Voice:** Adhering strictly to the character's defined speech patterns.
- **Environmental Awareness:** Integrating physical actions with the current location.

## 5. Frontend Requirements (Immersion Renderer)
- **Message Parsing:** The UI will map the `sequence` array to styled components:
    - `type: "thought"` -> *Italic, gray, smaller font.*
    - `type: "action"` -> **Bold, narrative style.**
    - `type: "speech"` -> Standard dialogue text.
- **User Profile UI:** A simple header or settings modal to set Name and Gender.
- **Stat HUD:** Visual bars for Energy, Hunger, and Relationship.

## 6. Testing & Validation
- **Unit Tests:** Verify `State-to-Behavior` mapping logic.
- **Integration Tests:** Ensure `User` data is correctly injected into prompts.
- **E2E Tests:** Verify the frontend correctly renders interleaved JSON sequences.

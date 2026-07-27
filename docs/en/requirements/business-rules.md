# Business Rules (RN) — Open-ChatBot

## RN-001: Personality Priority
The Character Prompt always takes precedence over the Master Prompt in case of stylistic conflict, provided it does not violate global safety constraints.

## RN-002: State-Behavior Thresholds
*   **Energy < 20%**: Forced narrative modifiers "sluggish", "irritable", "fatigued".
*   **Hunger > 80%**: Character dialogue must prioritize food-related context or show high impatience.
*   **Relationship > 80%**: Activates the "Close" behavioral layer (higher warmth and openness), always within global safety constraints.

## RN-003: Formatting Enforced
Any AI output that fails to include at least one Thought (`*...*`) or Action (`**...**`) in a response longer than 50 words is flagged for re-generation or client-side warning.

## RN-004: Memory Retention
User-specific facts (Name, Preferences) must persist until the User explicitly deletes their profile. Character "Reflections" are summarized every 20 messages to prevent context bloat.

## RN-005: Audit Trail
Every API request must be logged with a unique `request_id`, linking the User, Character, and the generated response for quality assurance and compliance debugging.

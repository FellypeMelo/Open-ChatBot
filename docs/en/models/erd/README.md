# Entity Relationship Diagrams (ERD)

The Open-ChatBot database (`chatbot.db`) is managed via SQLAlchemy ORM. Below is the relational structure of the tables and their constraints.

## 1. Relational Entity Schema

### A. Users Table (`users`)
*   `id` (Integer, Primary Key, Indexed)
*   `name` (String, Indexed)
*   `gender` (String)
*   `is_active` (Boolean, Default: `True`)

### B. Characters Table (`characters`)
*   `id` (Integer, Primary Key, Indexed)
*   `name` (String, Indexed)
*   `description` (Text)
*   `short_description` (Text)
*   `persona_prompt` (Text)
*   `is_active` (Boolean, Default: `True`)
*   *Relationships:*
    *   `tags`: Many-to-Many via `character_tags` junction.
    *   `state`: One-to-One with `AgentState`.

### C. Agent States Table (`agent_states`)
*   `id` (Integer, Primary Key, Indexed)
*   `character_id` (Integer, Foreign Key to `characters.id`, Unique, Indexed)
*   `current_message_id` (Integer, Foreign Key to `message_nodes.id`, Nullable)
*   `interaction_count` (Integer, Default: `0`)
*   `location` (String, Default: `"Living Room"`)
*   `mood` (String, Default: `"Neutral"`)
*   `clothes` (String, Default: `"Casual"`)
*   `stats` (JSON) - Stores dynamic needs (`energy`, `hunger`, `happiness`, `social`, `is_sleeping`, and `relationship` metadata).

### D. Message Nodes Table (`message_nodes`)
*   `id` (Integer, Primary Key, Indexed)
*   `parent_id` (Integer, Foreign Key to `message_nodes.id`, Nullable) - Self-referential for branching conversation threads.
*   `role` (String) - `'user'` or `'assistant'`.
*   `content` (Text) - Raw dialogue content.
*   `type` (String, Default: `"speech"`) - `'speech'`, `'thought'`, or `'action'`.
*   `variant_index` (Integer, Default: `0`) - For path variation index tracking.
*   `request_id` (String, Indexed, Nullable) - Correlates requests.
*   `character_id` (Integer, Foreign Key to `characters.id`, Indexed)
*   `user_id` (Integer, Foreign Key to `users.id`, Indexed, Nullable)

### E. Tags Table (`tags`)
*   `id` (Integer, Primary Key, Indexed)
*   `label` (String, Unique, Indexed)
*   `instruction` (Text) - The prompt snippet injected into the generator context.

### F. Character Tags Table (`character_tags` - Junction)
*   `character_id` (Integer, Foreign Key to `characters.id`, Primary Key)
*   `tag_id` (Integer, Foreign Key to `tags.id`, Primary Key)

### G. Lorebook Entries Table (`lorebook_entries`)
*   `id` (Integer, Primary Key, Indexed)
*   `keyword` (String, Indexed)
*   `content` (Text)
*   `character_id` (Integer, Foreign Key to `characters.id`, Nullable, Indexed)
*   `is_global` (Boolean, Default: `False`)

### H. Journal Entries Table (`journal_entries`)
*   `id` (Integer, Primary Key, Indexed)
*   `character_id` (Integer, Foreign Key to `characters.id`, Indexed)
*   `timestamp` (DateTime, Default: UTC `now`)
*   `content` (Text)
*   `summary` (Text)
*   `mood_at_time` (String)
*   `relationship_score` (Integer)
*   `energy_level` (Integer)

## 2. Key Cardinalities
1.  **Character $\leftrightarrow$ AgentState**: $1:1$ (Each character tracks one state container).
2.  **Character $\leftrightarrow$ MessageNode**: $1:N$ (A character has many message responses).
3.  **Character $\leftrightarrow$ Tag**: $M:N$ via `character_tags` junction.
4.  **MessageNode $\leftrightarrow$ MessageNode**: $1:N$ (Self-referential parent-child link for threaded branches).
5.  **Character $\leftrightarrow$ JournalEntry**: $1:N$ (A character records daily thoughts over time).


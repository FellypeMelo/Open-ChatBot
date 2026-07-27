# Diagramas de Entidade-Relacionamento (ERD)

O banco de dados do Open-ChatBot (`chatbot.db`) é gerenciado via ORM SQLAlchemy. Abaixo está a estrutura relacional das tabelas e suas constraints.

## 1. Schema de Entidades Relacionais

### A. Tabela Users (`users`)
*   `id` (Integer, Primary Key, Indexed)
*   `name` (String, Indexed)
*   `gender` (String)
*   `is_active` (Boolean, Default: `True`)

### B. Tabela Characters (`characters`)
*   `id` (Integer, Primary Key, Indexed)
*   `name` (String, Indexed)
*   `description` (Text)
*   `short_description` (Text)
*   `persona_prompt` (Text)
*   `is_active` (Boolean, Default: `True`)
*   *Relacionamentos:*
    *   `tags`: Muitos-para-Muitos via junction `character_tags`.
    *   `state`: Um-para-Um com `AgentState`.

### C. Tabela Agent States (`agent_states`)
*   `id` (Integer, Primary Key, Indexed)
*   `character_id` (Integer, Foreign Key para `characters.id`, Unique, Indexed)
*   `current_message_id` (Integer, Foreign Key para `message_nodes.id`, Nullable)
*   `interaction_count` (Integer, Default: `0`)
*   `location` (String, Default: `"Living Room"`)
*   `mood` (String, Default: `"Neutral"`)
*   `clothes` (String, Default: `"Casual"`)
*   `stats` (JSON) - Armazena necessidades dinâmicas (`energy`, `hunger`, `happiness`, `social`, `is_sleeping`, e metadados de `relationship`).

### D. Tabela Message Nodes (`message_nodes`)
*   `id` (Integer, Primary Key, Indexed)
*   `parent_id` (Integer, Foreign Key para `message_nodes.id`, Nullable) - Autorreferencial para ramificação de threads de conversa.
*   `role` (String) - `'user'` ou `'assistant'`.
*   `content` (Text) - Conteúdo bruto do diálogo.
*   `type` (String, Default: `"speech"`) - `'speech'`, `'thought'`, ou `'action'`.
*   `variant_index` (Integer, Default: `0`) - Para rastreamento de índice de variação de caminho.
*   `request_id` (String, Indexed, Nullable) - Correlaciona requisições.
*   `character_id` (Integer, Foreign Key para `characters.id`, Indexed)
*   `user_id` (Integer, Foreign Key para `users.id`, Indexed, Nullable)

### E. Tabela Tags (`tags`)
*   `id` (Integer, Primary Key, Indexed)
*   `label` (String, Unique, Indexed)
*   `instruction` (Text) - O trecho de prompt injetado no contexto do gerador.

### F. Tabela Character Tags (`character_tags` - Junction)
*   `character_id` (Integer, Foreign Key para `characters.id`, Primary Key)
*   `tag_id` (Integer, Foreign Key para `tags.id`, Primary Key)

### G. Tabela Lorebook Entries (`lorebook_entries`)
*   `id` (Integer, Primary Key, Indexed)
*   `keyword` (String, Indexed)
*   `content` (Text)
*   `character_id` (Integer, Foreign Key para `characters.id`, Nullable, Indexed)
*   `is_global` (Boolean, Default: `False`)

### H. Tabela Journal Entries (`journal_entries`)
*   `id` (Integer, Primary Key, Indexed)
*   `character_id` (Integer, Foreign Key para `characters.id`, Indexed)
*   `timestamp` (DateTime, Default: UTC `now`)
*   `content` (Text)
*   `summary` (Text)
*   `mood_at_time` (String)
*   `relationship_score` (Integer)
*   `energy_level` (Integer)

## 2. Cardinalidades-Chave
1.  **Character $\leftrightarrow$ AgentState**: $1:1$ (Cada personagem rastreia um container de estado).
2.  **Character $\leftrightarrow$ MessageNode**: $1:N$ (Um personagem tem muitas respostas de mensagem).
3.  **Character $\leftrightarrow$ Tag**: $M:N$ via junction `character_tags`.
4.  **MessageNode $\leftrightarrow$ MessageNode**: $1:N$ (Link autorreferencial pai-filho para ramificações em thread).
5.  **Character $\leftrightarrow$ JournalEntry**: $1:N$ (Um personagem registra pensamentos diários ao longo do tempo).

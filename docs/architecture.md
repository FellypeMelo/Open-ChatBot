# Architecture

Open-ChatBot is a local, self-hosted, single-user stateful AI character/RP engine.
FastAPI + SQLAlchemy + SQLite backend, React + TS + Vite frontend, and a local
`llama-server` (llama.cpp) providing both inference and embeddings. This describes
the flows that span many files; for the schema see [data-model-er.md](./data-model-er.md).

## Composition root

App-wide singletons `llama_client`, `vector_store`, `brain` are built once in
`core/deps.py` and imported everywhere. Never construct your own — separate
instances mean divergent in-memory vector stores over the same path, so a memory
added via one is invisible to another until restart.

## The chat turn

```mermaid
sequenceDiagram
    participant C as Client
    participant API as api/chat.py
    participant Brain as Brain.build_prompt
    participant LL as llama-server
    participant BG as run_consciousness_layer (bg)
    C->>API: POST /chat or /chat/stream
    API->>API: _prepare_chat_turn: resolve user/character/state/chat
    API->>API: need-decay + action deltas; validate parent_id
    API->>API: persist user message; walk active-branch history
    API->>Brain: build_prompt(state, history, lore, memory, budget)
    Brain->>LL: query_memory (RAG) + tokenize (budget)
    API->>LL: complete / complete_stream
    LL-->>API: reply
    API->>API: parse_actions_to_state; _persist_assistant_reply (retry on StaleData)
    API->>BG: schedule run_consciousness_layer
    BG->>LL: store memory; on interval, reflect + evolve
```

`_prepare_chat_turn` is shared by both `POST /chat` and `POST /chat/stream` so the
two paths can't diverge. Reflection is checkpoint-based:
`force_reflect = interaction_count - last_reflected_at_count >= REFLECTION_INTERVAL`
(a failed boundary reflection is retried, not skipped forever).

## Two-layer state (the mirror)

A character has one `AgentState` holding the **live** persona; each `Chat` is a
separate storyline and the **canonical** store of its conversation-local fields +
persona snapshot. `AgentState` mirrors the active chat; switching saves the
outgoing snapshot and restores the incoming one. Persona is **per-chat** (B8):
independent storylines. See [data-model-er.md](./data-model-er.md) §2.

## Memory lifecycle (anti-poison)

- **Scope:** every memory, history walk, and journal is scoped to
  `(character_id, chat_id)` so one chat can never poison another.
- **Storage:** RAG memories live in a turbovec store on disk (not the relational
  DB), linked to messages only by `message_id` metadata. Purged manually on
  edit/delete/regenerate.
- **Retrieval (`query_memory`):** over-fetch → relevance-threshold gate →
  cosine+recency blended re-rank → near-duplicate dedup → drop memories already
  visible in recent history. Results assembled into the prompt are sanitized
  against role-marker injection and length-capped.
- **Bounding:** when a chat scope exceeds the cap, the oldest memories are
  condensed by the LLM into one consolidated memory (store-before-delete).
- **Durability:** `_atomic_dump` writes to a temp dir then swaps, so a crash
  can't leave a torn store.

## Prompt assembly (`core/orchestration/bridge.py`)

An ultra-compact layered prompt for small local models, token-budgeted by
`core/context/budget.py` (fixed per-layer caps + a history floor). Layers: RAG
memory + lorebook (regex keys with word boundaries, scan_depth, secondary keys,
cooldown) + rolling `active_summary` + compressed state + history. Every free-text
card/persona field is sanitized and length-capped.

## Reflection / evolution (`core/engine/engine.py`)

`run_consciousness_layer` (background task) stores the turn's memory and, on
interval, calls `brain.reflect` (GBNF-constrained JSON) then `evolve_character`.
Evolution applies the reflection (relationship delta, facts, traits, tag
warmth-layering, rolling summary, journal, location/mood) inside a
`with_for_update` + version-guarded transaction with `StaleDataError` retries. If
the user switched chats during the slow reflect(), the reflection is applied to
the *reflecting* chat's snapshot, never the now-active one.

## llama-server runner (`core/engine/runner.py`)

Auto-starts a consolidated local llama-server (inference + embeddings on one port,
default 8080) from `models_config.json` on startup, health-gated with a warmup
poll. Bypassed entirely under pytest/E2E.

## Serving

`main.py` registers routers (chat, characters, tags, users, settings, lore,
presets) and mounts the built frontend from `static/` with an SPA catch-all — API
routes are registered before the catch-all.

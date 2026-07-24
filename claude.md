# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Open-ChatBot is a local, self-hosted, single-user stateful AI character/RP engine. FastAPI + SQLAlchemy + SQLite backend, React + TS + Vite + Tailwind frontend, and a local `llama-server` (llama.cpp) providing both inference and embeddings.

## Commands

Environment: Windows + PowerShell. The backend runs from a project-local virtualenv; invoke it explicitly (do **not** rely on a global `python`).

**Backend (Python / pytest / ruff):**
- Run all backend tests: `venv/Scripts/python.exe -m pytest src/backend/__tests__ -q`
- Single test / pattern: `venv/Scripts/python.exe -m pytest src/backend/__tests__/test_file.py::test_name -q` or `... -k "substring"`
- Lint: `venv/Scripts/python.exe -m ruff check src/backend`
- Backend only (no llama-server): `venv/Scripts/python.exe -m uvicorn src.backend.main:app --host 127.0.0.1 --port 8000`

**Frontend (pnpm only — never npm/yarn; run from `src/frontend`):**
- `pnpm dev` · `pnpm build` (tsc + vite → outputs to `static/`) · `pnpm lint` (eslint)
- Unit tests: `pnpm test` (vitest run) · watch: `pnpm test:watch` · coverage: `pnpm coverage`
- Single unit test: `pnpm vitest run src/path/File.test.tsx -t "test name"`
- E2E: `pnpm exec playwright test`

**Full app:** `run.sh` (Linux/mac) / `run.bat` (Windows) — builds the frontend, boots the consolidated llama-server on :8080, health-checks it, then starts uvicorn on :8000 (defaults to LAN-reachable `0.0.0.0`; pass `local` to bind localhost). The backend also auto-starts/stops llama-server itself via the FastAPI lifespan (skipped under tests).

## Architecture — the big picture

This is the non-obvious structure that spans many files. Read this before changing chat/memory/state code.

**Composition root (`core/deps.py`).** App-wide singletons `llama_client`, `vector_store`, `brain` are constructed once here and imported everywhere. Never build your own `VectorStore`/`Brain`/`LlamaClient` in a router — separate instances mean divergent in-memory vector stores pointing at the same path, so a memory added via one is invisible to another until restart.

**Two-layer conversational state (the "mirror" — most bug-prone area).** A character has exactly one `AgentState` (1:1, `unique character_id`) holding its **persistent persona**: `stats` JSON (energy/hunger/`relationship.score`/facts/discovered_traits/evolved_tags/`last_update`), location/mood/clothes, and an optimistic-concurrency `version` (`version_id_col`). Each `Chat` row is a separate session and is the **canonical** store of the *conversation-local* fields: `current_message_id`, `active_summary`, `interaction_count`, `last_reflected_at_count`. `AgentState` **mirrors the active chat's** copy of those live; switching chats saves the outgoing chat's snapshot and loads the incoming one (`_sync_state_to_chat` / `_load_chat_into_state`). Consequence: persona/relationship is **shared across all of a character's chats**; only the pointer/summary/counter is per-chat. Any edit/delete of a message in a *background* chat must target the **owning chat's** row, not the live `AgentState` (see `_set_branch_pointer`), or it corrupts the foreground chat's pointer.

**Per-`(character_id, chat_id)` scoping is the core anti-poison invariant.** History, RAG memories, and journals are all scoped so one chat can never leak into another. Legacy rows predating the `Chat` entity have `NULL chat_id` and are adopted into a lazily-created first chat.

**Message tree (`MessageNode`).** A `parent_id` chain with **soft-delete only** (`is_active=False`, never hard-delete — `parent_id` has no `ondelete`, so a hard delete would orphan children). Regenerate creates sibling variants under the same parent (`variant_index`, swipe model). The "active branch" is the parent chain walked back from the selected leaf; reflection and history walk that branch so discarded edit/regenerate branches never leak into state.

**RAG memory lives OUTSIDE the relational DB (`core/memory/vector_store.py`).** A quantized turbovec store persisted to disk (`CHROMA_PATH`, redirected to an isolated dir under tests). Memories link to messages **only by a `message_id` value in metadata — no FK** — so they are purged *manually* on edit/delete/regenerate (`delete_by_message_ids`). Anti-poison + quality lives here: relevance-threshold gate, cosine+recency blended ranking, near-duplicate dedup, `_atomic_dump` (crash-safe persistence), and a per-scope cap with **LLM consolidation of the oldest memories** (store-before-delete, never lose a batch).

**Turn flow (`api/chat.py`).** `_prepare_chat_turn` is shared by `POST /chat` and `POST /chat/stream`: resolve user/character/state/chat, apply need-decay + quick-action stat deltas, validate the `parent_id` (reject missing/deactivated/cross-thread), persist the user message, walk the active-branch history, and build the prompt. The reply is saved via `_persist_assistant_reply` (retries on `StaleDataError`). A background task `run_consciousness_layer` then stores the turn's memory, runs a **cheap per-turn scene extractor** (`Brain.extract_scene` → `apply_scene_update`, a tiny GBNF `{location, mood}` call, mirror-aware, decoupled from reflection so the HUD/anchor track the scene every turn — skipped under pytest), and, on interval, reflects+evolves. `force_reflect = interaction_count - last_reflected_at_count >= REFLECTION_INTERVAL` (checkpoint-based, not modulo, so a failed boundary reflection is retried, not skipped forever). **`Character.dynamic_persona` gates the simulation**: dynamic (default) applies need-decay + reflection evolution; static freezes both (persona as authored). Scene tracking + memory recall run in both modes.

**Prompt assembly (`core/orchestration/bridge.py` → `Brain.build_prompt`).** An ultra-compact layered prompt for small local models, token-budgeted by `core/context/budget.py`. Layers: E.P.I.C. master prompt (`COMPRESSED_MASTER_PROMPT` — stay-in-voice, react to the user, drive+escalate tension, sensory beats, end-with-hook, adaptive length) → identity/persona/scenario → tags → user persona → compressed state (`core/context/compressor.py`) → RAG memory + lorebook (`core/context/lorebook_scanner.py`, regex keys with word boundaries, scan_depth, secondary keys) → rolling `active_summary` → example dialogs → history → **recency anchor** (`_build_anchor`: persona-essence + current location/mood re-stated right before `Reply:`, so the persona sits at BOTH ends — a 4B attends to the start/end and loses the middle). Every free-text card/persona field is sanitized against role-marker injection; the colon-strip does the work, so **newlines are preserved** (card section headers/bullets survive). Card fields are capped only at `CARD_MAX_TOKENS` (generous safety, not the old 300) with a sentence-boundary cut; `RECOMMENDED_CARD_TOKENS` (4096) is a soft UI hint. History is bounded to `HISTORY_WINDOW_TOKENS` even on a large context (older turns carried by summary + RAG). Reflection AND the per-turn scene extractor use GBNF-constrained JSON grammars. `compress_state` renders relationship as a warmth **dial** ("in your own voice"), not a generic override, and physicality is bidirectional (high energy → alert). Context defaults to 48k in `models_config.json`.

**Reflection / evolution (`core/engine/engine.py`).** `evolve_character` applies the reflection JSON (relationship delta, facts, traits, tag warmth-layering, rolling summary, journal entry) inside a `with_for_update` + version-guarded transaction with `StaleDataError` retries. SQLAlchemy JSON gotcha: `stats` is a plain `JSON` column — assign-then-mutate loses in-place edits, so reassign `agent.stats = ...` **last**, after all mutations.

**llama-server runner (`core/engine/runner.py`).** Auto-starts a consolidated local llama-server (inference + embeddings on one port, default 8080) from `models_config.json` on startup; health-gated with a warmup poll. Bypassed entirely under pytest/E2E.

**Serving.** `main.py` registers routers (`chat`, `characters`, `tags`, `users`, `settings`, `lore`, `presets`) and mounts the built frontend from `static/` with an SPA catch-all — API routes are registered *before* the catch-all.

## Essential rules

1. **Package manager**: ALWAYS `pnpm` (never npm/yarn) for all frontend work.
2. **Shell**: Windows/PowerShell — write PowerShell-compatible syntax (`Remove-Item`, `New-Item`, not `rm`/`touch`).
3. **Test isolation**: NEVER touch the production DB (`chatbot.db`) or real `chroma_db` in tests. Tests use an isolated temp SQLite (`conftest.py`) and a redirected `CHROMA_PATH`; the app's lifespan skips `init_db`/llama boot under pytest. Keep new tests fully isolated (no real llama-server, no real embeddings, no prod DB).
4. **Coverage**: keep ≥80% for both backend and frontend, overall and per major module; new features ship with tests. Prefer test-first for correctness fixes.
5. **Migrations**: schema is managed by Alembic; `init_db` still carries manual `ALTER TABLE` compat. Generate a migration for any schema change; never run migrations against the real DB automatically — the user runs `alembic upgrade head`.

## Frontend design taste

1. **Layout**: `min-h-[100dvh]` (not `h-screen`) for hero/viewport sections; CSS Grid (`grid grid-cols-...`) over flexbox percent-math; mobile menus collapse cleanly under `768px` via overlay sidebar/modal.
2. **Typography**: prefer `Outfit` (sans display) + `JetBrains Mono`; avoid `Inter` as default. Emphasis via bold/italic of the *same* family — don't mix serif/sans in one header.
3. **Color**: max 1 accent over neutral bases (Zinc/Stone/Slate); one theme locked across the whole page (no light section inside a dark page).
4. **Controls/CTAs**: WCAG AA contrast; CTA labels fit one line at desktop width; consistent corner-radius scale.

## Corrections log

| Date | Correction | How to avoid |
| :--- | :--- | :--- |
| 2026-06-22 | Used `npm run test` instead of `pnpm`. | Always `pnpm` in this workspace. |
| 2026-07-17 | Began executing when the user had asked a question. | A question is not approval — answer first, then ask before acting. |

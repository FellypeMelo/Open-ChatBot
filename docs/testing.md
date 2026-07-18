# Testing & Contributing

## Running tests

Backend (from the repo root; use the project venv, never a global `python`):

```bash
venv/Scripts/python.exe -m pytest src/backend/__tests__ -q          # all
venv/Scripts/python.exe -m pytest src/backend/__tests__/test_x.py::test_y -q   # one
venv/Scripts/python.exe -m pytest src/backend/__tests__ -k "substring" -q      # by pattern
venv/Scripts/python.exe -m ruff check src/backend                   # lint
```

Frontend (from `src/frontend`, `pnpm` only — never npm/yarn):

```bash
pnpm test            # vitest run
pnpm vitest run src/path/File.test.tsx -t "test name"   # one
pnpm coverage        # coverage
pnpm lint            # eslint
pnpm exec playwright test   # E2E
```

## Test isolation (mandatory)

Tests must **never** touch the production DB (`chatbot.db`) or the real vector
store (`chroma_db`):

- `conftest.py` gives each test an isolated temp SQLite; `settings.CHROMA_PATH` is
  redirected to a temp dir under tests; the app lifespan skips `init_db` and the
  llama boot under pytest.
- No test may hit a real llama-server or real embeddings. Use deterministic fakes
  (e.g. a hash-based embedding) or mocks.
- FK enforcement is OFF on the default test engine (it binds the `PRAGMA
  foreign_keys=ON` listener only to the app engine). Tests that need FK behavior
  use the `fk_session` fixture in `test_db_cascade.py`, which enables it.

## Coverage & standards

- Keep **≥80%** coverage for backend and frontend, overall and per major module.
  New features ship with tests; prefer test-first for correctness fixes.
- The codebase follows Clean Architecture / SOLID / DDD (see the README). Domain
  logic in `core/` is transport- and persistence-agnostic; the DB `Session` and
  LLM clients are injected.

## Adding a feature safely

1. Write the failing test first (a concrete failure scenario).
2. Implement the minimal change; keep the suite green and `ruff` clean.
3. For a **schema change**: update `models.py` **and** generate an Alembic
   migration (`alembic revision -m "..."`); never run migrations against the real
   DB automatically — the user runs `alembic upgrade head`. See
   [data-model-er.md](./data-model-er.md) §"Schema management".
4. For risky changes to the chat/memory/state core, read
   [architecture.md](./architecture.md) first — the Chat↔AgentState mirror and the
   per-`(character, chat)` scoping are the most bug-prone areas.

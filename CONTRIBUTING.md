# Contributing to Open-ChatBot

Thanks for taking the time to contribute. This is a solo-maintained project, so please open an issue to discuss anything non-trivial (new features, architecture changes) before writing a large PR — it saves both of us time if the direction turns out to be wrong.

## Ground rules

* **Frontend package manager is `pnpm`, always.** Never `npm` or `yarn`. Run frontend commands from `src/frontend`.
* **Backend uses a project-local virtualenv.** Invoke it explicitly (`venv/Scripts/python.exe` on Windows, `venv/bin/python` on Linux/macOS) rather than relying on a global `python`.
* **Schema changes go through Alembic.** `src/backend/db/database.py:init_db()` also carries a manual `ALTER TABLE` compatibility path for existing databases — if you add/change a SQLAlchemy model, generate an Alembic migration for it; don't rely on `Base.metadata.create_all()` alone.
* **Test isolation is non-negotiable.** Tests must never touch the real `chatbot.db` or the real vector store directory. Use the fixtures in `conftest.py` (backend) and the existing test setup (frontend) — they redirect both to isolated temp locations.
* **Coverage floor is 80%**, backend and frontend, enforced in CI (`--cov-fail-under=80`). New features should ship with tests; prefer test-first for bug fixes so the regression is captured.

## Setup

```bash
# Backend
python -m venv venv
# Windows: venv\Scripts\activate  |  Linux/macOS: source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd src/frontend && pnpm install
```

You will also need your own GGUF model file and a `llama-server` binary to actually run the app end-to-end — see the [Quickstart in README.md](README.md#quickstart). Most backend unit tests do **not** require a running `llama-server`; the app's lifespan and the LLM client are bypassed under pytest.

## Running the checks locally before you open a PR

These are exactly the gates `.github/workflows/qa.yml` and `.github/workflows/e2e.yml` run on every push/PR to `main`:

```bash
# Backend lint + format
venv/Scripts/python.exe -m ruff check .
venv/Scripts/python.exe -m ruff format --check .

# Backend tests + coverage gate
venv/Scripts/python.exe -m pytest --cov=src --cov-report=term-missing --cov-fail-under=80

# Frontend (from src/frontend)
pnpm lint
pnpm build
pnpm coverage          # vitest run --coverage
pnpm exec playwright test
```

The backend test job also runs on `windows-latest` in CI (this project has real `win32`-only code paths in `src/backend/core/engine/runner.py`), so if you're on Linux/macOS and touch anything OS-sensitive, call it out in your PR description.

## Commit style

The project loosely follows [Conventional Commits](https://www.conventionalcommits.org/) (`feat(scope): ...`, `fix(scope): ...`, `docs: ...`, `test: ...`, `chore: ...`) — not strictly enforced, but preferred for a readable history.

## Opening a pull request

* Keep PRs focused on one change; large mixed refactors are hard to review and hard to revert.
* Fill in the PR template checklist — it mirrors the CI gates above.
* If your change touches the prompt-assembly/memory pipeline (`core/orchestration/bridge.py`, `core/memory/vector_store.py`), read [CLAUDE.md](CLAUDE.md) first — it documents the non-obvious invariants (per-`(character_id, chat_id)` scoping, soft-delete-only message tree, the two-layer conversational-state "mirror") that are easy to break silently.

## Reporting bugs or requesting features

Use the issue templates under `.github/ISSUE_TEMPLATE/`. For security vulnerabilities, do **not** open a public issue — see [SECURITY.md](SECURITY.md).

## Code of conduct

Participation in this project is governed by [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

# Continuous Integration & Delivery (CI/CD)

Open-ChatBot enforces its quality gates both locally and in CI. Two GitHub Actions workflows run on every push and pull request to `main`, and again nightly at 02:00 UTC:

*   **[`.github/workflows/qa.yml`](../../../.github/workflows/qa.yml)** — Ruff lint (`ruff check .`) and format check (`ruff format --check .`); backend `pytest` with `--cov-fail-under=80`, run on **both** `ubuntu-latest` and `windows-latest` (this project has real `win32`-only code paths, e.g. `src/backend/core/engine/runner.py`); frontend `pnpm lint`, `pnpm build`, and `pnpm coverage` (Vitest).
*   **[`.github/workflows/e2e.yml`](../../../.github/workflows/e2e.yml)** — builds the frontend, installs Playwright browsers, runs the full E2E suite (`src/frontend/e2e`) with `E2E_TESTING=1` to bypass local LLM-server boot, then smoke-tests the built static frontend by booting `uvicorn` and checking for an HTTP 200.

Coverage reports are uploaded as CI run artifacts (`actions/upload-artifact`) for inspection but are not published to a public coverage service or badge.

## 1. Quality Gates (Pre-commit / Build Checks)

### A. Backend Quality Verification
Backend validation is driven by Python `pytest` and `pytest-cov`. 
*   **Database Isolation Rules:** Tests must not connect to the production SQLite database (`chatbot.db`). Mocking must be used or an ephemeral `:memory:` database must be configured in `conftest.py`.
*   **Coverage Target:** Standard mandates minimum **80% code coverage** across backend modules.
*   **Execution Command:**
    ```bash
    pytest --cov=src/backend src/backend/__tests__/
    ```

### B. Frontend Quality Verification
Frontend validation is built on React Testing Library, Vitest, and ESLint.
*   **Package Manager Restriction:** Developers **must** use `pnpm` exclusively (never `npm` or `yarn`) to install dependencies and run scripts to maintain look-and-feel lock-in.
*   **Quality Checks:**
    - Linting: `pnpm lint`
    - Testing: `pnpm test` (Runs `vitest run`)
    - Coverage Audit: `pnpm coverage` (Runs `vitest run --coverage`)

## 2. Deployment Pipeline
Since this is a local desktop application, the build process bundles React into static assets:
1.  **Frontend Compilation:** Run `pnpm build` in `src/frontend` to output compile assets.
2.  **Asset Distribution:** Vite outputs static bundles to `static/` directory in the project root.
3.  **FastAPI Mount:** The FastAPI backend serves the compiled HTML and static bundles directly on start:
    ```python
    app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")
    ```
4.  **Local Execution:** Run `run.bat` (Windows PowerShell/CMD) or `run.sh` (Linux/Mac) to bootstrap FastAPI and spin up the local `llama-server.exe` instances.

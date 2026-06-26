# Continuous Integration & Delivery (CI/CD)

Open-ChatBot enforces strict quality gates on local builds before deployment. There is currently no cloud CI workflow (GitHub Actions) configured, but the project is structured to enforce standard test automation routines.

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

# Integração e Entrega Contínua (CI/CD)

O Open-ChatBot aplica seus quality gates tanto localmente quanto em CI. Dois workflows do GitHub Actions rodam em todo push e pull request para `main`, e novamente toda noite às 02:00 UTC:

*   **[`.github/workflows/qa.yml`](../../../.github/workflows/qa.yml)** — lint do Ruff (`ruff check .`) e verificação de formatação (`ruff format --check .`); `pytest` do backend com `--cov-fail-under=80`, rodando em **ambos** `ubuntu-latest` e `windows-latest` (este projeto tem código real específico de `win32`, ex.: `src/backend/core/engine/runner.py`); `pnpm lint`, `pnpm build` e `pnpm coverage` (Vitest) do frontend.
*   **[`.github/workflows/e2e.yml`](../../../.github/workflows/e2e.yml)** — builda o frontend, instala os navegadores do Playwright, roda a suíte E2E completa (`src/frontend/e2e`) com `E2E_TESTING=1` para pular o boot do servidor LLM local, e então faz um smoke test do frontend estático já buildado subindo o `uvicorn` e verificando um HTTP 200.

Os relatórios de cobertura são enviados como artifacts da execução de CI (`actions/upload-artifact`) para inspeção, mas não são publicados em um serviço público de cobertura ou badge.

## 1. Quality Gates (Verificações de Pré-commit / Build)

### A. Verificação de Qualidade do Backend
A validação do backend é conduzida pelo `pytest` e `pytest-cov` do Python.
*   **Regras de Isolamento de Banco:** Os testes não podem se conectar ao banco SQLite de produção (`chatbot.db`). Mocking deve ser usado, ou um banco `:memory:` efêmero deve ser configurado em `conftest.py`.
*   **Meta de Cobertura:** O padrão exige um mínimo de **80% de cobertura de código** nos módulos do backend.
*   **Comando de Execução:**
    ```bash
    pytest --cov=src/backend src/backend/__tests__/
    ```

### B. Verificação de Qualidade do Frontend
A validação do frontend é construída sobre React Testing Library, Vitest e ESLint.
*   **Restrição de Gerenciador de Pacotes:** Desenvolvedores **devem** usar o `pnpm` exclusivamente (nunca `npm` ou `yarn`) para instalar dependências e rodar scripts, mantendo o look-and-feel travado.
*   **Verificações de Qualidade:**
    - Lint: `pnpm lint`
    - Testes: `pnpm test` (roda `vitest run`)
    - Auditoria de Cobertura: `pnpm coverage` (roda `vitest run --coverage`)

## 2. Pipeline de Implantação
Como esta é uma aplicação desktop local, o processo de build empacota o React em assets estáticos:
1.  **Compilação do Frontend:** Rode `pnpm build` em `src/frontend` para gerar os assets compilados.
2.  **Distribuição de Assets:** O Vite emite bundles estáticos no diretório `static/` na raiz do projeto.
3.  **Montagem no FastAPI:** O backend FastAPI serve o HTML compilado e os bundles estáticos diretamente ao iniciar:
    ```python
    app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")
    ```
4.  **Execução Local:** Rode `run.bat` (Windows PowerShell/CMD) ou `run.sh` (Linux/Mac) para inicializar o FastAPI e subir as instâncias locais do `llama-server.exe`.

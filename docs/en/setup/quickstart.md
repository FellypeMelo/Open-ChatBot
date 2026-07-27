# Setup & Quickstart

This consolidates the setup/run steps that otherwise live scattered across the root `README.md`, `CLAUDE.md`/`GEMINI.md`, `run.sh`/`run.bat`, `.env.example`, and `models_config.example.json`. If any of those files and this page disagree, the files in the repository are the source of truth — this page just puts them in one place.

## What you need to supply yourself

Open-ChatBot does **not** bundle a model or an inference engine. Before anything runs, you need:

* A `llama-server` binary — from [llama.cpp](https://github.com/ggml-org/llama.cpp), or the author's own [llama-cpp-turboquant-SYCL](https://github.com/FellypeMelo/llama-cpp-turboquant-SYCL) fork if you want the optional 2-4 bit KV-cache quantization mode (`turbo3`) on Intel Arc/SYCL hardware.
* A GGUF model file of your choice.
* Python >= 3.10 (CI is pinned to 3.11) and Node.js with [`pnpm`](https://pnpm.io/) installed globally. This project uses `pnpm` exclusively for the frontend — `npm`/`yarn` are not supported workflows.
* Optional: GPU acceleration drivers for your `llama-server` build (e.g. Intel oneAPI, CUDA). Both run scripts try to load an Intel oneAPI environment (`setvars.bat`/`setvars.sh`) if present, but proceed without it if it isn't installed.

## 1. Backend environment

```bash
python -m venv venv
# Windows: venv\Scripts\activate  |  Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
```

## 2. Frontend dependencies

```bash
cd src/frontend && pnpm install && cd ../..
```

## 3. Point the app at your own model

Copy the two example config files and edit them:

```bash
cp .env.example .env
cp models_config.example.json models_config.json
```

`.env.example` (backend runtime config):

```
LLAMA_SERVER_URL=http://localhost:8080
DATABASE_URL=sqlite:///./chatbot.db
MODEL_PATH=models/your-model.gguf
```

`models_config.example.json` (the `llama-server` process launcher config — inference and embedding sections, typically pointed at the same consolidated server/port):

```json
{
  "inference": {
    "binary_path": "llama_bin/llama-server.exe",
    "model_path": "models/model.gguf",
    "port": 8080,
    "threads": 0,
    "gpu_layers": 99,
    "context_size": 65536,
    "additional_args": "--cache-type-k turbo3 --cache-type-v turbo3 --flash-attn on --parallel 1 --ubatch-size 2048"
  },
  "embedding": {
    "binary_path": "llama_bin/llama-server.exe",
    "model_path": "models/model.gguf",
    "port": 8080,
    "threads": 0,
    "gpu_layers": 99,
    "context_size": 65536,
    "additional_args": "--cache-type-k turbo3 --cache-type-v turbo3 --flash-attn on --parallel 1 --ubatch-size 2048"
  }
}
```

Edit both files to point `MODEL_PATH` / `binary_path` / `model_path` at your own `llama-server` binary and `.gguf` file. The `turbo3` cache-type flags in `additional_args` are specific to the author's turboquant-SYCL fork — drop them if you're running stock `llama.cpp`.

## 4. Run it

```bash
# Windows (PowerShell or cmd)
run.bat

# Linux / macOS
chmod +x run.sh
./run.sh
```

Both scripts build the frontend (`pnpm build` in `src/frontend`) before starting the API. `run.sh` additionally starts the consolidated `llama-server` process itself and waits for its `/health` endpoint before continuing; on the backend, `core/engine/runner.py` also auto-starts and health-gates a `llama-server` instance from `models_config.json` on FastAPI startup (see [infrastructure/sre.md](../infrastructure/sre.md)) — check your own setup if you run both paths together to avoid starting the server twice.

Both scripts default to binding `0.0.0.0` (LAN-reachable, so a phone on the same Wi-Fi can connect) and print the LAN URL on startup. Pass `local` (`run.bat local` / `./run.sh local`) to bind `127.0.0.1` only. **There is no login of any kind** — anyone who can reach the bound address can use the app, so only enable LAN mode on networks you trust. `run.sh` additionally accepts `--debug`, which sets `DEBUG_LATENCY=True` and raises the `uvicorn` log level for step-by-step latency diagnostics.

To run the backend alone, without either run script:

```bash
venv/Scripts/python.exe -m uvicorn src.backend.main:app --host 127.0.0.1 --port 8000
```

## 5. Database migrations

`init_db()` builds/updates the schema on startup and stamps it at the current Alembic revision if it isn't tracked yet. Schema changes are versioned via Alembic (`src/backend/db/migrations/`); after pulling changes that touch the schema, run the migration yourself — it is never applied automatically:

```bash
venv/Scripts/python.exe -m alembic upgrade head
```

## Next steps

* [testing.md](../testing.md) — running the test suites and adding a feature safely.
* [card-authoring-epic.md](../card-authoring-epic.md) — writing a character card.
* [mobile-lan-smoke-test.md](../mobile-lan-smoke-test.md) — the manual mobile-device checklist for LAN mode.

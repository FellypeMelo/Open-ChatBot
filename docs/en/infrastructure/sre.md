# Site Reliability Engineering & Operations (SRE)

Open-ChatBot operates as a local service, with specific reliability, health checking, and optimization practices implemented directly inside the application lifecycle.

## 1. Local Process & Service Management
The FastAPI application acts as the process manager for the AI engines.
*   **Auto-Orchestration:** Upon launch, the backend reads configuration from `models_config.json` and invokes the [LlamaServerRunner](../../../src/backend/core/engine/runner.py) to spin up a single unified `llama-server.exe` instance.
*   **Consolidated Server Mode:** By default, both inference and embeddings use the same model and share port `8080`. The runner automatically detects this and launches only one `llama-server.exe` process with the `--embedding` flag enabled to handle both roles, significantly saving VRAM/RAM allocations.
*   **Lifespan Shutdown Hook:** When the FastAPI instance is stopped, it calls `runner.stop_all()` to terminate the running background `llama-server.exe` instance, avoiding zombie processes. See [main.py](../../../src/backend/main.py).

## 2. Health Monitoring & Verification
*   **Startup Verification:** During application startup, the server performs embedding and inference health checks via [LlamaClient](../../../src/backend/core/engine/llm.py).
*   **Degraded State Contingency:** If the embedding server is unreachable, the system writes a `WARNING` log and continues running in a degraded state with memory retrieval features disabled, preventing complete application failure.

## 3. Storage Reliability & Optimizations
*   **SQLite Vacuuming:** On startup, the backend calls `vacuum_db()` which executes the SQL command `VACUUM` asynchronously. This reduces disk fragmentation and reclaims unused database space, ensuring long-term filesystem health. See [database.py](../../../src/backend/db/database.py).
*   **Vector Database Bit Width:** To manage performance constraints on local consumer hardware, the TurboQuant vector database index uses a **4-bit quantization width** (`bit_width=4`) to store embeddings, reducing RAM utilization and speeding up cosine similarity searches. See [vector_store.py](../../../src/backend/core/memory/vector_store.py).

## 4. Troubleshooting Logs
Standard application logs are captured by Python's `logging` module. Real-time request timings are optionally measured (if `settings.DEBUG_LATENCY` is enabled) to log step-by-step latency bottlenecks.

import logging
import asyncio
import re
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from src.backend.api import (
    chat,
    characters,
    tags,
    users,
    settings as api_settings,
    lore,
    presets,
)
from src.backend.db.database import init_db, seed_default_presets
from src.backend.core.engine.llm import LlamaClient
from src.backend.core.engine.runner import runner
from src.backend.core.config import settings

# Ensure all logs (including runner diagnostics) are visible in console
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    import os

    # Pytest's TestClient overrides the DB dependency with its own isolated
    # engine (see conftest.py) while this app's own module-level `engine`
    # still points at the real chatbot.db -- running init_db()/vacuum_db()
    # here would touch production data on every test that spins up the app
    # (violates the test-isolation rule). E2E runs are different: E2E_TESTING
    # redirects DATABASE_URL to its own e2e_test.db (see core/config.py), so
    # init_db() there is creating schema in that isolated file, not touching
    # anything real -- skipping it would leave e2e_test.db with no tables.
    is_pytest = settings.TESTING
    is_e2e = os.environ.get("E2E_TESTING") == "1"
    is_testing = is_pytest or is_e2e

    if not is_pytest:
        # Startup: Initialize DB
        logger.info("Initializing database...")
        init_db()
        seed_default_presets()

        # Reclaim unused database space
        from src.backend.db.database import vacuum_db

        vacuum_db()

    # Auto-start the real llama-server (unless running tests or E2E mode --
    # E2E_TESTING bypasses LLM server boot in the backend entirely).
    if not is_testing:
        logger.info("Auto-starting Llama servers from settings...")
        inf_ok = runner.start_inference()
        logger.info(f"start_inference returned: {inf_ok}")
        emb_ok = runner.start_embedding()
        logger.info(f"start_embedding returned: {emb_ok}")

        if not inf_ok:
            logger.error(
                "CRITICAL: Llama Inference Server failed to start! Check logs/llama_inference.log"
            )

        logger.info("Checking LLM server health...")
        llama = LlamaClient()

        health = {"inference": False, "embedding": False}
        is_consolidated = (
            runner.config["embedding"]["port"] == runner.config["inference"]["port"]
        )

        # Poll up to 30 seconds (model loading on GPU can take 20+ seconds)
        for attempt in range(1, 31):
            health = await llama.health_check()
            if health["inference"] and (is_consolidated or health["embedding"]):
                break
            logger.warning(
                f"Waiting for Llama server to respond (attempt {attempt}/30)..."
            )
            await asyncio.sleep(1)

        if not health["inference"]:
            logger.error("CRITICAL: Llama Inference Server is unreachable!")
        else:
            logger.info("Llama Inference Server is healthy.")

        if not health["embedding"]:
            logger.warning(
                "Llama Embedding Server is unreachable! Memory features will be disabled."
            )
        else:
            logger.info("Llama Embedding Server is healthy.")

        await llama.close()
    yield

    # Shutdown logic
    if not is_testing:
        logger.info("Shutting down llama-server processes...")
        runner.stop_all()
    logger.info("Shutting down Open-ChatBot...")


app = FastAPI(title="Open-ChatBot", lifespan=lifespan)

app.include_router(chat.router)
app.include_router(characters.router, prefix="/characters", tags=["Characters"])
app.include_router(tags.router, prefix="/tags", tags=["Tags"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(api_settings.router, prefix="/settings", tags=["Settings"])
app.include_router(lore.router, prefix="/lore", tags=["Lore"])
app.include_router(presets.router, prefix="/presets", tags=["Presets"])

# Mount static files (Frontend) - API routes MUST come first
import os


class ImmutableStaticFiles(StaticFiles):
    """StaticFiles that marks every served file cacheable forever.

    Vite content-hashes every filename under /assets (e.g.
    index-CDFjAh1V.js), so a given URL's bytes never change -- a rebuild
    produces new filenames instead. That makes it safe for phones on a slow
    or flaky LAN connection to cache these responses indefinitely and never
    re-request them, instead of re-validating (or re-downloading) the whole
    JS/CSS/font bundle on every load.
    """

    def file_response(self, *args, **kwargs):
        response = super().file_response(*args, **kwargs)
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return response


os.makedirs("static/avatars", exist_ok=True)
os.makedirs("static/assets", exist_ok=True)
app.mount("/assets", ImmutableStaticFiles(directory="static/assets"), name="assets")
app.mount("/avatars", StaticFiles(directory="static/avatars"), name="avatars")


@app.get("/favicon.svg")
async def favicon():
    return FileResponse("static/favicon.svg")


@app.get("/manifest.webmanifest")
async def manifest():
    return FileResponse(
        "static/manifest.webmanifest", media_type="application/manifest+json"
    )


# The service worker (sw.js) and its hashed Workbox runtime chunk
# (workbox-<hash>.js) are written by vite-plugin-pwa to the build root
# alongside index.html -- NOT under /assets -- because a service worker's
# default scope is the directory it is served from, and it must be served
# from "/" to control the whole single-page app. Without this, they would
# fall through to the catch-all below and be served as index.html
# (text/html), which fails SW registration outright.
_PWA_RUNTIME_FILENAME_RE = re.compile(r"^(sw\.js|workbox-[\w-]+\.js)$")


@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    if _PWA_RUNTIME_FILENAME_RE.match(full_path):
        pwa_file_path = os.path.join("static", full_path)
        if os.path.isfile(pwa_file_path):
            response = FileResponse(pwa_file_path, media_type="application/javascript")
            # Always revalidate the SW script itself so a rebuild is picked
            # up promptly -- the precached shell it references is still
            # immutable/content-hashed, only this small entry file isn't.
            response.headers["Cache-Control"] = "no-cache"
            return response

    response = FileResponse("static/index.html")
    # index.html is the one file in the SPA that is NEVER content-hashed, so
    # it is the single point of failure for the "stale index.html points at
    # deleted hashed asset filenames" class of bug: a rebuild changes every
    # /assets/* filename, and a cached old index.html would keep requesting
    # asset URLs that no longer exist. Forcing revalidation on every load
    # (and disallowing any shared/disk cache from serving it without
    # asking) guarantees a rebuild is always reflected on next load, while
    # the actually-immutable hashed assets above are still cached forever.
    response.headers["Cache-Control"] = "no-store, must-revalidate"
    return response

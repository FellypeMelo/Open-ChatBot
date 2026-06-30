import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from src.backend.api import chat, characters, tags, users, settings as api_settings, lore, presets
from src.backend.db.database import init_db
from src.backend.core.engine.llm import LlamaClient
from src.backend.core.engine.runner import runner

# Ensure all logs (including runner diagnostics) are visible in console
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB
    logger.info("Initializing database...")
    init_db()
    
    import os
    os.makedirs("static/avatars", exist_ok=True)
    
    # Reclaim unused database space
    from src.backend.db.database import vacuum_db
    vacuum_db()
    
    # Auto-start servers using LlamaServerRunner (unless running tests or E2E mode)
    import sys
    import os
    is_testing = "pytest" in sys.modules or os.environ.get("E2E_TESTING") == "1"
    if not is_testing:
        logger.info("Auto-starting Llama servers from settings...")
        inf_ok = runner.start_inference()
        logger.info(f"start_inference returned: {inf_ok}")
        emb_ok = runner.start_embedding()
        logger.info(f"start_embedding returned: {emb_ok}")
        
        if not inf_ok:
            logger.error("CRITICAL: Llama Inference Server failed to start! Check logs/llama_inference.log")
        
        logger.info("Checking LLM server health...")
        llama = LlamaClient()
        
        health = {"inference": False, "embedding": False}
        is_consolidated = runner.config["embedding"]["port"] == runner.config["inference"]["port"]
        
        # Poll up to 30 seconds (model loading on GPU can take 20+ seconds)
        for attempt in range(1, 31):
            health = await llama.health_check()
            if health["inference"] and (is_consolidated or health["embedding"]):
                break
            logger.warning(f"Waiting for Llama server to respond (attempt {attempt}/30)...")
            await asyncio.sleep(1)
        
        if not health["inference"]:
            logger.error("CRITICAL: Llama Inference Server is unreachable!")
        else:
            logger.info("Llama Inference Server is healthy.")
            
        if not health["embedding"]:
            logger.warning("Llama Embedding Server is unreachable! Memory features will be disabled.")
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
os.makedirs("static/avatars", exist_ok=True)
app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")
app.mount("/avatars", StaticFiles(directory="static/avatars"), name="avatars")

@app.get("/favicon.svg")
async def favicon():
    return FileResponse("static/favicon.svg")

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    return FileResponse("static/index.html")

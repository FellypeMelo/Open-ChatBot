import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from src.backend.api import chat, characters, tags, users, settings as api_settings
from src.backend.db.database import init_db
from src.backend.core.engine.llm import LlamaClient
from src.backend.core.engine.runner import runner

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB
    logger.info("Initializing database...")
    init_db()
    
    # Reclaim unused database space
    from src.backend.db.database import vacuum_db
    vacuum_db()
    
    # Auto-start servers using LlamaServerRunner (unless running tests)
    import sys
    is_testing = "pytest" in sys.modules
    if not is_testing:
        logger.info("Auto-starting Llama servers from settings...")
        runner.start_inference()
        runner.start_embedding()
        # Give them 2 seconds to spin up before health check
        await asyncio.sleep(2)
    
    if not is_testing:
        logger.info("Checking LLM server health...")
        llama = LlamaClient()
        health = await llama.health_check()
        
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

# Mount static files (Frontend) - API routes MUST come first
app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")

@app.get("/favicon.svg")
async def favicon():
    return FileResponse("static/favicon.svg")

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    return FileResponse("static/index.html")

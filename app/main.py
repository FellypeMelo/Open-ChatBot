import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api import chat, characters, tags, users
from app.db.database import init_db
from app.core.llm import LlamaClient

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB and Check LLM health
    logger.info("Initializing database...")
    init_db()
    
    logger.info("Checking LLM server health...")
    llama = LlamaClient()
    health = await llama.health_check()
    
    if not health["inference"]:
        logger.error("CRITICAL: Llama Inference Server (port 8080) is unreachable!")
    else:
        logger.info("Llama Inference Server is healthy.")
        
    if not health["embedding"]:
        logger.warning("Llama Embedding Server (port 8081) is unreachable! Memory features will be disabled.")
    else:
        logger.info("Llama Embedding Server is healthy.")
        
    await llama.close()
    yield
    # Shutdown logic (if any) can go here
    logger.info("Shutting down Open-ChatBot...")

app = FastAPI(title="Open-ChatBot", lifespan=lifespan)

app.include_router(chat.router)
app.include_router(characters.router, prefix="/characters", tags=["Characters"])
app.include_router(tags.router, prefix="/tags", tags=["Tags"])
app.include_router(users.router, prefix="/users", tags=["Users"])

# Mount static files (Frontend) - API routes MUST come first
app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")

@app.get("/favicon.svg")
async def favicon():
    return FileResponse("static/favicon.svg")

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    return FileResponse("static/index.html")

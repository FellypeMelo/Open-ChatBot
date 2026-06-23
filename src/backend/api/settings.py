import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
from src.backend.core.engine.runner import runner

logger = logging.getLogger(__name__)

router = APIRouter()

class ServerConfigModel(BaseModel):
    binary_path: str
    model_path: str
    port: int
    threads: int
    gpu_layers: int
    context_size: int = 4096
    additional_args: str

class LlamaConfigModel(BaseModel):
    inference: ServerConfigModel
    embedding: ServerConfigModel

@router.get("/status")
async def get_runner_status():
    try:
        return runner.get_status()
    except Exception as e:
        logger.error(f"Failed to get runner status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/save")
async def save_runner_config(config: LlamaConfigModel):
    try:
        runner.config["inference"] = config.inference.model_dump()
        runner.config["embedding"] = config.embedding.model_dump()
        runner.save_config()
        return {"status": "success", "message": "Configuration saved successfully."}
    except Exception as e:
        logger.error(f"Failed to save runner config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start/inference")
async def start_inference_server():
    success = runner.start_inference()
    if success:
        return {"status": "success", "message": "Inference server started."}
    else:
        raise HTTPException(status_code=500, detail="Failed to start inference server. Check logs.")

@router.post("/stop/inference")
async def stop_inference_server():
    try:
        runner.stop_inference()
        return {"status": "success", "message": "Inference server stopped."}
    except Exception as e:
        logger.error(f"Failed to stop inference server: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start/embedding")
async def start_embedding_server():
    success = runner.start_embedding()
    if success:
        return {"status": "success", "message": "Embedding server started."}
    else:
        raise HTTPException(status_code=500, detail="Failed to start embedding server. Check logs.")

@router.post("/stop/embedding")
async def stop_embedding_server():
    try:
        runner.stop_embedding()
        return {"status": "success", "message": "Embedding server stopped."}
    except Exception as e:
        logger.error(f"Failed to stop embedding server: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/restart-all")
async def restart_all_servers():
    try:
        inf_success = runner.start_inference()
        emb_success = runner.start_embedding()
        return {
            "status": "success",
            "message": "Servers restarted.",
            "inference": inf_success,
            "embedding": emb_success
        }
    except Exception as e:
        logger.error(f"Failed to restart servers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

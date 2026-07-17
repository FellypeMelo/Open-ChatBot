import asyncio
import logging
import re
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from src.backend.core.engine.runner import runner
from src.backend.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Reject shell/control metacharacters in additional_args. args.split() already
# passes tokens straight into Popen's argv (never through a shell), so this
# isn't closing a shell-injection hole -- it's a defensive floor in case that
# ever changes, and it catches obviously-malformed input either way.
_UNSAFE_ARG_CHARS = re.compile(r"[;&|`$<>\n\r]")


class ServerConfigModel(BaseModel):
    binary_path: str
    model_path: str
    port: int
    threads: int
    gpu_layers: int
    context_size: int = settings.CONTEXT_SIZE
    additional_args: str

    @field_validator("binary_path")
    @classmethod
    def _binary_must_be_known(cls, v: str) -> str:
        name = Path(v).name
        available = runner.get_available_binaries()
        if name not in available:
            raise ValueError(
                f"binary_path must be one of the binaries in llama_bin/: {available}"
            )
        return f"llama_bin/{name}"

    @field_validator("model_path")
    @classmethod
    def _model_must_be_known_or_hf(cls, v: str) -> str:
        if not v:
            return v
        p = Path(v)
        is_hf = "/" in v and not v.startswith("models/") and not p.is_absolute()
        if is_hf:
            return v
        name = p.name
        if name not in runner.get_available_models():
            raise ValueError(
                f"model_path must be a file in models/, or an org/repo HuggingFace id: {v}"
            )
        return f"models/{name}"

    @field_validator("additional_args")
    @classmethod
    def _no_shell_metacharacters(cls, v: str) -> str:
        if _UNSAFE_ARG_CHARS.search(v):
            raise ValueError("additional_args contains disallowed characters")
        return v


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
    success = await asyncio.to_thread(runner.start_inference)
    if success:
        return {"status": "success", "message": "Inference server started."}
    else:
        raise HTTPException(
            status_code=500, detail="Failed to start inference server. Check logs."
        )


@router.post("/stop/inference")
async def stop_inference_server():
    try:
        await asyncio.to_thread(runner.stop_inference)
        return {"status": "success", "message": "Inference server stopped."}
    except Exception as e:
        logger.error(f"Failed to stop inference server: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start/embedding")
async def start_embedding_server():
    success = await asyncio.to_thread(runner.start_embedding)
    if success:
        return {"status": "success", "message": "Embedding server started."}
    else:
        raise HTTPException(
            status_code=500, detail="Failed to start embedding server. Check logs."
        )


@router.post("/stop/embedding")
async def stop_embedding_server():
    try:
        await asyncio.to_thread(runner.stop_embedding)
        return {"status": "success", "message": "Embedding server stopped."}
    except Exception as e:
        logger.error(f"Failed to stop embedding server: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/restart-all")
async def restart_all_servers():
    try:
        inf_success = await asyncio.to_thread(runner.start_inference)
        emb_success = await asyncio.to_thread(runner.start_embedding)
        return {
            "status": "success",
            "message": "Servers restarted.",
            "inference": inf_success,
            "embedding": emb_success,
        }
    except Exception as e:
        logger.error(f"Failed to restart servers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class TokenizeRequest(BaseModel):
    text: str


@router.post("/tokenize")
async def tokenize_text(payload: TokenizeRequest):
    try:
        from src.backend.core.deps import brain
        count = await brain.budget_calc.count_tokens(payload.text)
        return {"tokens": count}
    except Exception as e:
        logger.error(f"Failed to tokenize text: {e}")
        raise HTTPException(status_code=500, detail=str(e))

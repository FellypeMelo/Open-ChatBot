from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.llm import LlamaClient

router = APIRouter()
llama = LlamaClient()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        result = await llama.complete(request.message)
        return ChatResponse(reply=result.get("content", ""))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

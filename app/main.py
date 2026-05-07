from fastapi import FastAPI
from app.api import chat

app = FastAPI(title="Open-ChatBot")

app.include_router(chat.router)

@app.get("/")
async def root():
    return {"message": "Open-ChatBot API is running"}

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api import chat, characters, tags
from app.db.database import engine, Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Open-ChatBot")

app.include_router(chat.router)
app.include_router(characters.router, prefix="/characters", tags=["Characters"])
app.include_router(tags.router, prefix="/tags", tags=["Tags"])

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api import chat, characters, tags, users
from app.db.database import init_db

# Create tables
init_db()

app = FastAPI(title="Open-ChatBot")

app.include_router(chat.router)
app.include_router(characters.router, prefix="/characters", tags=["Characters"])
app.include_router(tags.router, prefix="/tags", tags=["Tags"])
app.include_router(users.router, prefix="/users", tags=["Users"])

# Mount static files (Frontend)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

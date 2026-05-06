import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import init_db

# Initialize database tables BEFORE importing routers that depend on the DB
init_db()

from backend.routers import conversations, chat

app = FastAPI(title="AI Chatbot API", version="1.0.0")

# CORS — allow native app and web browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(conversations.router)
app.include_router(chat.router)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ping")
def ping():
    return {"status": "alive"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

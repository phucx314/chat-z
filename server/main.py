import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from server.routers import conversations, chat

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

# Serve web frontend from /web
WEB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web")
if os.path.isdir(WEB_DIR):
    app.mount("/web", StaticFiles(directory=WEB_DIR, html=True), name="web")

    @app.get("/")
    def root():
        return FileResponse(os.path.join(WEB_DIR, "index.html"))

@app.get("/health")
def health():
    return {"status": "ok"}

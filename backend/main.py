import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import chat, conversations, auth
from backend.database import init_db

app = FastAPI(title="Chat-Z Backend")

# Initialize database on startup
@app.on_event("startup")
def on_startup():
    init_db()

# Cấu hình CORS để cho phép Frontend ở domain khác gọi vào và gửi kèm Cookie
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://chat-z-client.pages.dev",
        # Allow all origins dynamically using a regex if necessary, but allow_credentials requires exact origins or regex.
        # For simplicity since Vercel/Pages often have random subdomains during preview:
        "*" if not os.getenv("RENDER") else "https://chat-z-client.pages.dev"
    ] if os.getenv("RENDER") else ["http://localhost:3000", "https://chat-z-client.pages.dev"],
    allow_origin_regex=r"https://chat-z-client.*\.pages\.dev", # Match any preview URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/wakeup")
def wakeup():
    return {"status": "alive"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
app.include_router(chat.router)
app.include_router(conversations.router)

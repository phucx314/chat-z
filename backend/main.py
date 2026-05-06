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

# Cấu hình CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://chat-z-client.pages.dev",
]

# Thêm FRONTEND_URL từ environment variable nếu có
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    # Hỗ trợ tự động TẤT CẢ các link preview sinh ra sau mỗi lần deploy FE (ví dụ: https://c8b24d1d.chat-z-client.pages.dev)
    allow_origin_regex=r"https?://(?:.*\.)?chat-z-client\.pages\.dev",
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

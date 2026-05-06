import os
from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.types import JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import func
from dotenv import load_dotenv

ENV_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(ENV_FILE, override=False)

# Support Render Postgres URL format or fallback to local SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/chatbot.db")

# Handle Render's postgres:// instead of postgresql:// for SQLAlchemy
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

is_sqlite = DATABASE_URL.startswith("sqlite")

connect_args = {"check_same_thread": False} if is_sqlite else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ConversationModel(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, default="New Chat")
    avatar_color = Column(String, default="#4f6ef7")
    messages = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    
    # We will add pgvector Vector column later when implementing semantic search
    # embedding = Column(Vector(384)) # e.g. for all-MiniLM-L6-v2

class ConfigModel(Base):
    __tablename__ = "app_config"
    
    key = Column(String, primary_key=True)
    value = Column(JSON)

def init_db():
    # Make sure the data directory exists if using sqlite
    if is_sqlite:
        os.makedirs(os.path.dirname(DATABASE_URL.replace("sqlite:///", "")), exist_ok=True)
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

import os
import uuid
from datetime import datetime
from backend.database import SessionLocal, ConversationModel

AVATAR_COLORS = [
    "#4f6ef7", "#e05678", "#25a56a", "#f07d3e",
    "#9b59b6", "#1abc9c", "#e74c3c", "#3498db",
    "#f39c12", "#d35400", "#8e44ad", "#16a085",
]

def get_all_conversations() -> list:
    with SessionLocal() as db:
        convs = db.query(ConversationModel).order_by(ConversationModel.updated_at.desc()).all()
        return [{"id": c.id, "title": c.title, "avatar_color": c.avatar_color, "messages": c.messages, "created_at": c.created_at.isoformat() if c.created_at else None, "updated_at": c.updated_at.isoformat() if c.updated_at else None} for c in convs]

def get_conversation(conv_id: str) -> dict | None:
    with SessionLocal() as db:
        c = db.query(ConversationModel).filter(ConversationModel.id == conv_id).first()
        if c:
            return {"id": c.id, "title": c.title, "avatar_color": c.avatar_color, "messages": c.messages, "created_at": c.created_at.isoformat() if c.created_at else None, "updated_at": c.updated_at.isoformat() if c.updated_at else None}
        return None

def create_conversation(title: str = "New Chat") -> dict:
    with SessionLocal() as db:
        count = db.query(ConversationModel).count()
        color = AVATAR_COLORS[count % len(AVATAR_COLORS)]
        new_conv = ConversationModel(
            id=str(uuid.uuid4()),
            title=title,
            avatar_color=color,
            messages=[]
        )
        db.add(new_conv)
        db.commit()
        db.refresh(new_conv)
        return {"id": new_conv.id, "title": new_conv.title, "avatar_color": new_conv.avatar_color, "messages": new_conv.messages, "created_at": new_conv.created_at.isoformat() if new_conv.created_at else None, "updated_at": new_conv.updated_at.isoformat() if new_conv.updated_at else None}

def update_conversation(conv_id: str, messages: list):
    """Update messages and auto-title from first user message."""
    with SessionLocal() as db:
        c = db.query(ConversationModel).filter(ConversationModel.id == conv_id).first()
        if c:
            # Need to reassign list for JSON column to detect change in SQLAlchemy sometimes
            c.messages = list(messages)
            first_user = next((m["content"] for m in messages if m["role"] == "user"), None)
            if first_user and c.title == "New Chat":
                c.title = first_user[:40].strip() + ("…" if len(first_user) > 40 else "")
            db.commit()

def rename_conversation(conv_id: str, title: str):
    with SessionLocal() as db:
        c = db.query(ConversationModel).filter(ConversationModel.id == conv_id).first()
        if c:
            c.title = title.strip()[:60]
            db.commit()

def update_avatar_color(conv_id: str, color: str):
    with SessionLocal() as db:
        c = db.query(ConversationModel).filter(ConversationModel.id == conv_id).first()
        if c:
            c.avatar_color = color
            db.commit()

def delete_conversation(conv_id: str):
    with SessionLocal() as db:
        db.query(ConversationModel).filter(ConversationModel.id == conv_id).delete()
        db.commit()

def delete_message(conv_id: str, message_index: int) -> list | None:
    """Delete a message by index. Returns updated messages list or None if invalid."""
    with SessionLocal() as db:
        c = db.query(ConversationModel).filter(ConversationModel.id == conv_id).first()
        if c:
            msgs = list(c.messages)
            if 0 <= message_index < len(msgs):
                msgs.pop(message_index)
                c.messages = msgs
                db.commit()
                db.refresh(c)
                return c.messages
    return None

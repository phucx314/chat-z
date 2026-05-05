import os
import json
import uuid
from datetime import datetime

HISTORY_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "history.json")

AVATAR_COLORS = [
    "#4f6ef7", "#e05678", "#25a56a", "#f07d3e",
    "#9b59b6", "#1abc9c", "#e74c3c", "#3498db",
    "#f39c12", "#d35400", "#8e44ad", "#16a085",
]

def _load_all() -> list:
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def _save_all(conversations: list):
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(conversations, f, ensure_ascii=False, indent=2)

def get_all_conversations() -> list:
    convs = _load_all()
    return sorted(convs, key=lambda c: c.get("updated_at", ""), reverse=True)

def get_conversation(conv_id: str) -> dict | None:
    for c in _load_all():
        if c["id"] == conv_id:
            return c
    return None

def create_conversation(title: str = "New Chat") -> dict:
    all_convs = _load_all()
    color = AVATAR_COLORS[len(all_convs) % len(AVATAR_COLORS)]
    conv = {
        "id": str(uuid.uuid4()),
        "title": title,
        "avatar_color": color,
        "messages": [],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    all_convs.append(conv)
    _save_all(all_convs)
    return conv

def update_conversation(conv_id: str, messages: list):
    """Update messages and auto-title from first user message."""
    all_convs = _load_all()
    for c in all_convs:
        if c["id"] == conv_id:
            c["messages"] = messages
            c["updated_at"] = datetime.now().isoformat()
            first_user = next((m["content"] for m in messages if m["role"] == "user"), None)
            if first_user and c["title"] == "New Chat":
                c["title"] = first_user[:40].strip() + ("…" if len(first_user) > 40 else "")
            break
    _save_all(all_convs)

def rename_conversation(conv_id: str, title: str):
    all_convs = _load_all()
    for c in all_convs:
        if c["id"] == conv_id:
            c["title"] = title.strip()[:60]
            c["updated_at"] = datetime.now().isoformat()
            break
    _save_all(all_convs)

def update_avatar_color(conv_id: str, color: str):
    all_convs = _load_all()
    for c in all_convs:
        if c["id"] == conv_id:
            c["avatar_color"] = color
            break
    _save_all(all_convs)

def delete_conversation(conv_id: str):
    all_convs = [c for c in _load_all() if c["id"] != conv_id]
    _save_all(all_convs)

def delete_message(conv_id: str, message_index: int) -> list | None:
    """Delete a message by index. Returns updated messages list or None if invalid."""
    all_convs = _load_all()
    for c in all_convs:
        if c["id"] == conv_id:
            msgs = c.get("messages", [])
            if 0 <= message_index < len(msgs):
                msgs.pop(message_index)
                c["messages"] = msgs
                c["updated_at"] = datetime.now().isoformat()
                _save_all(all_convs)
                return msgs
            return None
    return None

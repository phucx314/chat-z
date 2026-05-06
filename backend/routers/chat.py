import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import APIRouter, HTTPException, Depends
from backend.models import SendMessageRequest
from backend.services.config_service import load_config, get_effective_api_key, save_config
from backend.services.history_service import get_conversation, update_conversation
from backend.services.auth_service import get_current_user
from backend.database import UserModel
from ai.models import PROVIDERS
import json

router = APIRouter(tags=["chat"])

@router.get("/config")
def get_config(user: UserModel = Depends(get_current_user)):
    cfg = load_config(user.id)
    return {
        "provider":      cfg.get("provider", "OpenAI"),
        "model":         cfg.get("model", "gpt-4o-mini"),
        "base_url":      cfg.get("base_url", ""),
        "has_key":       bool(get_effective_api_key(cfg)),
        "key_from_env":  cfg.get("_key_from_env", False),
        "allow_interrupt": cfg.get("allow_interrupt", False),
        "providers":     {k: {"base_url": v["base_url"], "models": v["models"]}
                          for k, v in PROVIDERS.items()},
    }

@router.patch("/config")
def update_config(body: dict, user: UserModel = Depends(get_current_user)):
    cfg = load_config(user.id)
    if "provider" in body:
        cfg["provider"] = body["provider"]
        preset = PROVIDERS.get(body["provider"], {})
        if preset:
            cfg["base_url"] = preset["base_url"]
    if "model"    in body: cfg["model"]    = body["model"]
    if "base_url" in body: cfg["base_url"] = body["base_url"]
    if "api_key"  in body: cfg["api_key"]  = body["api_key"]
    if "allow_interrupt" in body: cfg["allow_interrupt"] = body["allow_interrupt"]
    save_config(user.id, cfg)
    return {"ok": True}

@router.post("/chat/send")
def send_message(body: SendMessageRequest, user: UserModel = Depends(get_current_user)):
    cfg = load_config(user.id)
    api_key = get_effective_api_key(cfg)
    if not api_key:
        raise HTTPException(401, "No API key configured")

    conv = get_conversation(body.conv_id, user.id)
    if not conv:
        raise HTTPException(404, "Conversation not found")

    messages = list(conv.get("messages", []))
    
    if body.override_messages is not None:
        messages = [{"role": m.role, "content": m.content} for m in body.override_messages]

    messages.append({"role": "user", "content": body.message})

    # Giới hạn số lượng tin nhắn gửi đi (Sliding Window) để tiết kiệm token
    MAX_HISTORY = 20
    context_messages = messages[-MAX_HISTORY:] if len(messages) > MAX_HISTORY else messages

    model    = body.model or cfg.get("model", "gpt-4o-mini")
    base_url = cfg.get("base_url", "").strip() or None

    try:
        from ai.engine import generate_reply
        reply = generate_reply(context_messages, model, api_key, base_url)
    except Exception as e:
        raise HTTPException(502, str(e))

    # Split reply aggressively: treat both [SPLIT] and newlines (\n) as message breaks
    # This prevents the AI from sending massive multi-paragraph blocks
    reply_normalized = reply.replace("[SPLIT]", "\n")
    replies = [r.strip() for r in reply_normalized.split("\n") if r.strip()]
    
    if not replies:
        replies = [reply]

    for r in replies:
        messages.append({"role": "assistant", "content": r})
    
    update_conversation(body.conv_id, user.id, messages)

    return {
        "replies":  replies,
        "messages": messages,
    }

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from server.models import SendMessageRequest
from core.config import load_config, get_effective_api_key, SYSTEM_PROMPT, save_config, PROVIDERS
from core.history import get_conversation, update_conversation
from openai import OpenAI
import json

router = APIRouter(tags=["chat"])

# In-memory config cache (loaded once, updated via /config endpoints)
_cfg = load_config()


def get_cfg():
    return _cfg


@router.get("/config")
def get_config():
    cfg = get_cfg()
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
def update_config(body: dict):
    global _cfg
    if "provider" in body:
        _cfg["provider"] = body["provider"]
        preset = PROVIDERS.get(body["provider"], {})
        if preset:
            _cfg["base_url"] = preset["base_url"]
    if "model"    in body: _cfg["model"]    = body["model"]
    if "base_url" in body: _cfg["base_url"] = body["base_url"]
    if "api_key"  in body: _cfg["api_key"]  = body["api_key"]
    if "allow_interrupt" in body: _cfg["allow_interrupt"] = body["allow_interrupt"]
    save_config(_cfg)
    return {"ok": True}


@router.post("/chat/send")
def send_message(body: SendMessageRequest):
    global _cfg
    cfg = get_cfg()
    api_key = get_effective_api_key(cfg)
    if not api_key:
        raise HTTPException(401, "No API key configured")

    conv = get_conversation(body.conv_id)
    if not conv:
        raise HTTPException(404, "Conversation not found")

    messages = list(conv.get("messages", []))
    
    if body.override_messages is not None:
        messages = [{"role": m.role, "content": m.content} for m in body.override_messages]

    messages.append({"role": "user", "content": body.message})

    model    = body.model or cfg.get("model", "gpt-4o-mini")
    base_url = cfg.get("base_url", "").strip() or None

    try:
        client = OpenAI(api_key=api_key, base_url=base_url)
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
            temperature=0.8,
        )
        reply = response.choices[0].message.content
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
    
    update_conversation(body.conv_id, messages)

    return {
        "replies":  replies,
        "messages": messages,
    }

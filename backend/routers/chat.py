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

    from ai.engine import generate_reply, get_embedding
    from backend.services.history_service import save_message_vector, search_similar_messages

    # 1. Generate embedding for current user message
    base_url = cfg.get("base_url", "").strip() or None
    try:
        user_embedding = get_embedding(body.message, api_key, base_url)
    except Exception as e:
        print(f"Warning: Failed to get user embedding: {e}")
        user_embedding = None

    # 2. Search for similar messages (RAG)
    context_msgs = []
    if user_embedding:
        try:
            context_msgs = search_similar_messages(body.conv_id, user_embedding, limit=5)
        except Exception as e:
            print(f"Warning: Failed to search similar messages: {e}")

    # 3. Construct prompt with RAG context
    # We still keep a small window of the most recent messages for conversational flow
    RECENT_WINDOW = 2
    recent_msgs = messages[-RECENT_WINDOW:] if len(messages) > RECENT_WINDOW else messages
    
    # Final context for LLM
    final_prompt_messages = []
    if context_msgs:
        # Filter out messages that are already in the recent window to avoid duplication
        recent_contents = [m['content'] for m in recent_msgs]
        unique_context = [m for m in context_msgs if m['content'] not in recent_contents]
        
        if unique_context:
            context_str = "\n".join([f"{m['role']}: {m['content']}" for m in unique_context])
            final_prompt_messages.append({
                "role": "system", 
                "content": f"Relevant past context (use only if needed):\n{context_str}"
            })
    
    final_prompt_messages.extend(recent_msgs)
    final_prompt_messages.append({"role": "user", "content": body.message})

    # DEBUG: Track payload size
    total_chars = sum(len(m['content']) for m in final_prompt_messages)
    print(f"DEBUG: Sending {len(final_prompt_messages)} messages to LLM. Total chars: {total_chars}")

    model    = body.model or cfg.get("model", "gpt-4o-mini")
    base_url = cfg.get("base_url", "").strip() or None

    try:
        reply = generate_reply(final_prompt_messages, model, api_key, base_url)
    except Exception as e:
        raise HTTPException(502, str(e))

    # 4. Save embeddings for future retrieval
    if user_embedding:
        try:
            # Save user message vector
            save_message_vector(body.conv_id, "user", body.message, user_embedding)
            
            # Save assistant reply vector
            reply_embedding = get_embedding(reply, api_key, base_url)
            save_message_vector(body.conv_id, "assistant", reply, reply_embedding)
        except Exception as e:
            print(f"Warning: Failed to save message vectors: {e}")

    # Process and save to full history for UI
    messages.append({"role": "user", "content": body.message})
    
    reply_normalized = reply.replace("[SPLIT]", "\n")
    replies = [r.strip() for r in reply_normalized.split("\n") if r.strip()]
    if not replies: replies = [reply]

    for r in replies:
        messages.append({"role": "assistant", "content": r})
    
    update_conversation(body.conv_id, user.id, messages)

    return {
        "replies":  replies,
        "messages": messages,
    }

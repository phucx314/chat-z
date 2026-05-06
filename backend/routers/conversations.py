import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import APIRouter, HTTPException
from backend.models import CreateConvRequest, RenameConvRequest, UpdateAvatarRequest
import backend.services.history_service as history

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("")
def list_conversations():
    return history.get_all_conversations()


@router.post("")
def create_conversation(body: CreateConvRequest):
    return history.create_conversation(body.title)


@router.get("/{conv_id}")
def get_conversation(conv_id: str):
    conv = history.get_conversation(conv_id)
    if not conv:
        raise HTTPException(404, "Conversation not found")
    return conv


@router.patch("/{conv_id}/rename")
def rename_conversation(conv_id: str, body: RenameConvRequest):
    if not history.get_conversation(conv_id):
        raise HTTPException(404, "Conversation not found")
    history.rename_conversation(conv_id, body.title)
    return {"ok": True}


@router.patch("/{conv_id}/avatar")
def update_avatar(conv_id: str, body: UpdateAvatarRequest):
    if not history.get_conversation(conv_id):
        raise HTTPException(404, "Conversation not found")
    history.update_avatar_color(conv_id, body.color)
    return {"ok": True}


@router.delete("/{conv_id}")
def delete_conversation(conv_id: str):
    if not history.get_conversation(conv_id):
        raise HTTPException(404, "Conversation not found")
    history.delete_conversation(conv_id)
    return {"ok": True}


@router.delete("/{conv_id}/messages/{message_index}")
def delete_message(conv_id: str, message_index: int):
    result = history.delete_message(conv_id, message_index)
    if result is None:
        raise HTTPException(400, "Invalid message index or conversation not found")
    return {"ok": True, "messages": result}

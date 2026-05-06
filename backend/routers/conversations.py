import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import APIRouter, HTTPException, Depends
from backend.models import CreateConvRequest, RenameConvRequest, UpdateAvatarRequest
from backend.services.auth_service import get_current_user
from backend.database import UserModel
import backend.services.history_service as history

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("")
def list_conversations(user: UserModel = Depends(get_current_user)):
    return history.get_all_conversations(user.id)


@router.post("")
def create_conversation(body: CreateConvRequest, user: UserModel = Depends(get_current_user)):
    return history.create_conversation(user.id, body.title)


@router.get("/{conv_id}")
def get_conversation(conv_id: str, user: UserModel = Depends(get_current_user)):
    conv = history.get_conversation(conv_id, user.id)
    if not conv:
        raise HTTPException(404, "Conversation not found")
    return conv


@router.patch("/{conv_id}/rename")
def rename_conversation(conv_id: str, body: RenameConvRequest, user: UserModel = Depends(get_current_user)):
    if not history.get_conversation(conv_id, user.id):
        raise HTTPException(404, "Conversation not found")
    history.rename_conversation(conv_id, user.id, body.title)
    return {"ok": True}


@router.patch("/{conv_id}/avatar")
def update_avatar(conv_id: str, body: UpdateAvatarRequest, user: UserModel = Depends(get_current_user)):
    if not history.get_conversation(conv_id, user.id):
        raise HTTPException(404, "Conversation not found")
    history.update_avatar_color(conv_id, user.id, body.color)
    return {"ok": True}


@router.delete("/{conv_id}")
def delete_conversation(conv_id: str, user: UserModel = Depends(get_current_user)):
    if not history.get_conversation(conv_id, user.id):
        raise HTTPException(404, "Conversation not found")
    history.delete_conversation(conv_id, user.id)
    return {"ok": True}


@router.delete("/{conv_id}/messages/{message_index}")
def delete_message(conv_id: str, message_index: int, user: UserModel = Depends(get_current_user)):
    result = history.delete_message(conv_id, user.id, message_index)
    if result is None:
        raise HTTPException(400, "Invalid message index or conversation not found")
    return {"ok": True, "messages": result}

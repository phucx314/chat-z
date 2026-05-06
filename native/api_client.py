import httpx
from PyQt6.QtCore import QThread, pyqtSignal

SERVER_URL = "http://localhost:8000"

class LLMWorker(QThread):
    finished = pyqtSignal(list, bool)   # list of texts, is_error

    def __init__(self, conv_id: str, message: str, model: str = None, override_messages: list = None, parent=None):
        super().__init__(parent)
        self.conv_id = conv_id
        self.message = message
        self.model   = model
        self.override_messages = override_messages

    def run(self):
        try:
            payload = {"conv_id": self.conv_id, "message": self.message}
            if self.model:
                payload["model"] = self.model
            if self.override_messages is not None:
                payload["override_messages"] = self.override_messages

            with httpx.Client(timeout=60) as client:
                res = client.post(f"{SERVER_URL}/chat/send", json=payload)

            if res.status_code == 200:
                data = res.json()
                replies = data.get("replies", [data.get("reply", "")])
                self.finished.emit(replies, False)
            elif res.status_code == 401:
                self.finished.emit(["⚠️ Chưa có API key. Vào Settings để thêm key."], True)
            else:
                detail = res.json().get("detail", res.text)
                self.finished.emit([f"❌ Lỗi server: {detail}"], True)

        except Exception as e:
            self.finished.emit([f"❌ Lỗi kết nối: {e}"], True)

class APIClient:
    """Centralized client for all Backend interactions."""
    
    @staticmethod
    def get_config():
        try:
            with httpx.Client(timeout=5) as c:
                res = c.get(f"{SERVER_URL}/config")
            return res.json() if res.status_code == 200 else {}
        except Exception:
            return {}

    @staticmethod
    def update_config(data: dict):
        try:
            with httpx.Client(timeout=5) as c:
                res = c.patch(f"{SERVER_URL}/config", json=data)
            return res.status_code == 200
        except Exception:
            return False

    @staticmethod
    def list_conversations():
        try:
            with httpx.Client(timeout=5) as c:
                res = c.get(f"{SERVER_URL}/conversations")
            return res.json() if res.status_code == 200 else []
        except Exception:
            return []

    @staticmethod
    def get_conversation(conv_id: str):
        try:
            with httpx.Client(timeout=5) as c:
                res = c.get(f"{SERVER_URL}/conversations/{conv_id}")
            return res.json() if res.status_code == 200 else None
        except Exception:
            return None

    @staticmethod
    def create_conversation(title: str = "New Chat"):
        try:
            with httpx.Client(timeout=5) as c:
                res = c.post(f"{SERVER_URL}/conversations", json={"title": title})
            return res.json() if res.status_code == 200 else None
        except Exception:
            return None

    @staticmethod
    def rename_conversation(conv_id: str, title: str):
        try:
            with httpx.Client(timeout=5) as c:
                res = c.patch(f"{SERVER_URL}/conversations/{conv_id}/rename", json={"title": title})
            return res.status_code == 200
        except Exception:
            return False

    @staticmethod
    def delete_conversation(conv_id: str):
        try:
            with httpx.Client(timeout=5) as c:
                res = c.delete(f"{SERVER_URL}/conversations/{conv_id}")
            return res.status_code == 200
        except Exception:
            return False

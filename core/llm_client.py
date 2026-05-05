"""
Native app LLM Worker — calls the local FastAPI server instead of OpenAI directly.
Falls back to direct OpenAI call if server is unreachable.
"""
from PyQt6.QtCore import QThread, pyqtSignal
import httpx


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
                self.finished.emit(
                    ["⚠️ Chưa có API key. Vào ⚙ Settings để thêm key."], True
                )
            else:
                detail = res.json().get("detail", res.text)
                self.finished.emit([f"❌ Lỗi server: {detail}"], True)

        except httpx.ConnectError:
            self.finished.emit([
                "❌ Không thể kết nối tới server.\n"
                "Hãy chạy server trước:\n\n"
                "  uvicorn server.main:app --reload --port 8000"
            ], True)
        except Exception as e:
            self.finished.emit([f"❌ Lỗi: {e}"], True)

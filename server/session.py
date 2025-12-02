import secrets
import time
from typing import Dict, Optional

import config


class SessionStore:
    """以内存字典保存会话信息"""

    def __init__(self) -> None:
        self._sessions: Dict[str, Dict[str, str]] = {}

    def create(self, user_id: int) -> str:
        """创建新的 session 并返回 session_id"""

        session_id = secrets.token_hex(16)
        self._sessions[session_id] = {
            "user_id": str(user_id),
            "expires": str(int(time.time()) + config.SESSION_EXPIRE_SECONDS),
        }
        return session_id

    def get_user_id(self, session_id: str) -> Optional[int]:
        """读取 session 对应的用户"""

        data = self._sessions.get(session_id)
        if not data:
            return None
        if int(data.get("expires", "0")) < int(time.time()):
            self.delete(session_id)
            return None
        return int(data["user_id"])

    def delete(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)


session_store = SessionStore()

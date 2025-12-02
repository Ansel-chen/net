from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class HttpResponse:
    """封装发送给浏览器的响应对象"""

    status_code: int = 200
    reason: str = "OK"
    headers: Dict[str, str] = field(default_factory=dict)
    body: bytes = b""

    _status_reason = {
        200: "OK",
        201: "Created",
        204: "No Content",
        302: "Found",
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        409: "Conflict",
        500: "Internal Server Error",
    }

    @classmethod
    def text(cls, content: str, status: int = 200, content_type: str = "text/html; charset=utf-8") -> "HttpResponse":
        """返回文本响应"""

        body = content.encode("utf-8")
        headers = {
            "Content-Type": content_type,
            "Content-Length": str(len(body)),
        }
        return cls(status_code=status, reason=cls._status_reason.get(status, "OK"), headers=headers, body=body)

    @classmethod
    def json(cls, payload: dict, status: int = 200) -> "HttpResponse":
        """返回 JSON 响应"""

        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Content-Length": str(len(body)),
        }
        return cls(status_code=status, reason=cls._status_reason.get(status, "OK"), headers=headers, body=body)

    @classmethod
    def redirect(cls, location: str) -> "HttpResponse":
        """构造 302 重定向"""

        headers = {"Location": location, "Content-Length": "0"}
        return cls(status_code=302, reason="Found", headers=headers, body=b"")

    def to_bytes(self) -> bytes:
        """序列化为符合 HTTP 规范的字节流"""

        self.headers.setdefault("Server", "MiniSocketBlog/0.1")
        self.headers.setdefault("Connection", "close")
        response_line = f"HTTP/1.1 {self.status_code} {self.reason}\r\n"
        header_lines = "".join(f"{k}: {v}\r\n" for k, v in self.headers.items())
        return (response_line + header_lines + "\r\n").encode("utf-8") + self.body

from __future__ import annotations

import json
import urllib.parse
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class HttpRequest:
    """封装客户端发来的 HTTP 请求"""

    method: str
    path: str
    version: str
    headers: Dict[str, str]
    query: Dict[str, str]
    body: bytes = field(default_factory=bytes)
    form: Dict[str, str] = field(default_factory=dict)
    json_data: Optional[dict] = None
    cookies: Dict[str, str] = field(default_factory=dict)
    client_addr: str = ""
    path_params: Dict[str, str] = field(default_factory=dict)

    @staticmethod
    def parse(raw_data: bytes, client_addr: str) -> "HttpRequest":
        """解析套接字收到的原始字节流"""

        try:
            header_blob, body = raw_data.split(b"\r\n\r\n", 1)
        except ValueError:
            header_blob = raw_data
            body = b""
        lines = header_blob.decode("utf-8", errors="ignore").split("\r\n")
        request_line = lines[0]
        method, url, version = request_line.split()
        path, _, query_string = url.partition("?")
        headers: Dict[str, str] = {}
        for line in lines[1:]:
            if not line:
                continue
            name, _, value = line.partition(":")
            headers[name.strip().lower()] = value.strip()
        query = dict(urllib.parse.parse_qsl(query_string))
        cookies = HttpRequest._parse_cookies(headers.get("cookie", ""))
        form: Dict[str, str] = {}
        json_data: Optional[dict] = None
        content_type = headers.get("content-type", "")
        if body:
            if "application/json" in content_type:
                try:
                    json_data = json.loads(body.decode("utf-8"))
                except json.JSONDecodeError:
                    json_data = None
            elif "application/x-www-form-urlencoded" in content_type:
                form = dict(urllib.parse.parse_qsl(body.decode("utf-8")))
        return HttpRequest(
            method=method.upper(),
            path=urllib.parse.unquote(path),
            version=version,
            headers=headers,
            query=query,
            body=body,
            form=form,
            json_data=json_data,
            cookies=cookies,
            client_addr=client_addr,
        )

    @staticmethod
    def _parse_cookies(cookie_header: str) -> Dict[str, str]:
        """拆分 Cookie 字符串"""

        cookies = {}
        for item in cookie_header.split(";"):
            item = item.strip()
            if not item:
                continue
            name, _, value = item.partition("=")
            cookies[name] = value
        return cookies

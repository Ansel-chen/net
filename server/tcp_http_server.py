from __future__ import annotations

import logging
import socket
import threading
from typing import Callable

import config
from .http_request import HttpRequest
from .http_response import HttpResponse
from .router import Router
from .static_handler import serve_static

logger = logging.getLogger(__name__)


class TcpHttpServer:
    """使用原生 TCP Socket 的迷你 HTTP 服务器"""

    def __init__(self, host: str, port: int, router: Router) -> None:
        self.host = host
        self.port = port
        self.router = router
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start(self) -> None:
        self._sock.bind((self.host, self.port))
        self._sock.listen(128)
        logger.info("服务器启动: %s:%s", self.host, self.port)
        while True:
            client_socket, addr = self._sock.accept()
            thread = threading.Thread(target=self._handle_client, args=(client_socket, addr), daemon=True)
            thread.start()

    def _handle_client(self, client_socket: socket.socket, addr) -> None:
        client_ip = f"{addr[0]}:{addr[1]}"
        try:
            raw_data = client_socket.recv(config.MAX_REQUEST_SIZE)
            if not raw_data:
                return
            request = HttpRequest.parse(raw_data, client_ip)
            if request.path.startswith("/static/"):
                response = serve_static(request.path)
            else:
                response = self.router.dispatch(request)
        except Exception as exc:  # pragma: no cover - 防御性日志
            logger.exception("处理请求出错: %s", exc)
            response = HttpResponse.text("服务器内部错误", status=500)
        finally:
            client_socket.sendall(response.to_bytes())
            client_socket.close()

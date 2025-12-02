from __future__ import annotations

import re
from typing import Any, Callable, Dict, List, Optional, Tuple

from .http_request import HttpRequest
from .http_response import HttpResponse

Handler = Callable[[HttpRequest], HttpResponse]


class Router:
    """最简路由器，支持路径参数"""

    def __init__(self) -> None:
        self._routes: List[Tuple[str, re.Pattern[str], Handler]] = []

    def add_route(self, method: str, pattern: str, handler: Handler) -> None:
        """注册路由，pattern 使用 {id} 形式定义参数"""

        regex_pattern = re.sub(r"{([^/]+)}", r"(?P<\1>[^/]+)", pattern)
        compiled = re.compile(f"^{regex_pattern}$")
        self._routes.append((method.upper(), compiled, handler))

    def resolve(self, request: HttpRequest) -> Tuple[Optional[Handler], Dict[str, str]]:
        """匹配路由并返回处理器与路径变量"""

        for method, pattern, handler in self._routes:
            if method != request.method:
                continue
            match = pattern.match(request.path)
            if match:
                request.path_params = match.groupdict()
                return handler, match.groupdict()
        return None, {}

    def dispatch(self, request: HttpRequest) -> HttpResponse:
        """根据请求分发到具体处理函数"""

        handler, _ = self.resolve(request)
        if handler is None:
            return HttpResponse.text("未找到资源", status=404)
        return handler(request)

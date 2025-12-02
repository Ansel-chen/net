from __future__ import annotations

from typing import Optional, Tuple

from server.http_request import HttpRequest
from server.http_response import HttpResponse

from .auth_controller import get_current_user


def require_login(request: HttpRequest) -> Tuple[Optional[dict], Optional[HttpResponse]]:
    """若未登录则直接返回 401"""

    user = get_current_user(request)
    if not user:
        return None, HttpResponse.json({"error": "需要先登录"}, status=401)
    return user, None

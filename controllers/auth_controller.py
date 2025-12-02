from __future__ import annotations

from server.http_request import HttpRequest
from server.http_response import HttpResponse
from server.session import session_store
from services import auth_service


def _require_fields(payload: dict, fields: list[str]) -> tuple[bool, str]:
    for field in fields:
        if not payload.get(field):
            return False, f"缺少字段 {field}"
    return True, ""


def register(request: HttpRequest) -> HttpResponse:
    data = request.json_data or request.form
    ok, msg = _require_fields(data, ["username", "password", "nickname"])
    if not ok:
        return HttpResponse.json({"error": msg}, status=400)
    try:
        user_id = auth_service.register(
            username=data["username"],
            password=data["password"],
            nickname=data["nickname"],
            email=data.get("email"),
        )
    except Exception as exc:
        return HttpResponse.json({"error": f"注册失败: {exc}"}, status=400)
    return HttpResponse.json({"user_id": user_id}, status=201)


def login(request: HttpRequest) -> HttpResponse:
    data = request.json_data or request.form
    ok, msg = _require_fields(data, ["username", "password"])
    if not ok:
        return HttpResponse.json({"error": msg}, status=400)
    session_id = auth_service.login(data["username"], data["password"])
    if not session_id:
        return HttpResponse.json({"error": "用户名或密码错误"}, status=401)
    resp = HttpResponse.json({"message": "登录成功"})
    resp.headers["Set-Cookie"] = f"session_id={session_id}; Path=/; HttpOnly"
    return resp


def logout(request: HttpRequest) -> HttpResponse:
    session_id = request.cookies.get("session_id")
    if session_id:
        session_store.delete(session_id)
    resp = HttpResponse.json({"message": "已退出"})
    resp.headers["Set-Cookie"] = "session_id=; Path=/; HttpOnly; Max-Age=0"
    return resp


def current_user(request: HttpRequest) -> HttpResponse:
    user = get_current_user(request)
    if not user:
        return HttpResponse.json({"user": None})
    safe_user = dict(user)
    safe_user.pop("password_hash", None)
    safe_user.pop("salt", None)
    return HttpResponse.json({"user": safe_user})


def get_current_user(request: HttpRequest):
    session_id = request.cookies.get("session_id")
    if not session_id:
        return None
    user_id = session_store.get_user_id(session_id)
    if not user_id:
        return None
    return auth_service.get_user(user_id)

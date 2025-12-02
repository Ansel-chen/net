from __future__ import annotations

from server.http_request import HttpRequest
from server.http_response import HttpResponse
from services import comment_service

from .utils import require_login


def list_comments(request: HttpRequest) -> HttpResponse:
    post_id = int(request.path_params.get("post_id"))
    comments = comment_service.list_comments(post_id)
    return HttpResponse.json({"items": comments})


def add_comment(request: HttpRequest) -> HttpResponse:
    user, error = require_login(request)
    if error:
        return error
    payload = request.json_data or request.form
    body = payload.get("body") if payload else None
    if not body:
        return HttpResponse.json({"error": "评论内容不能为空"}, status=400)
    post_id = int(request.path_params.get("post_id"))
    parent_id = payload.get("parent_id") if payload else None
    comment_id = comment_service.add_comment(post_id, user["id"], body, parent_id)
    return HttpResponse.json({"comment_id": comment_id}, status=201)

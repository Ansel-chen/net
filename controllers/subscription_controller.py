from __future__ import annotations

from server.http_request import HttpRequest
from server.http_response import HttpResponse
from services import subscription_service

from .utils import require_login


def follow_author(request: HttpRequest) -> HttpResponse:
    user, error = require_login(request)
    if error:
        return error
    author_id = int(request.path_params.get("author_id"))
    subscription_service.follow(user["id"], author_id)
    return HttpResponse.json({"message": "已关注"})


def unfollow_author(request: HttpRequest) -> HttpResponse:
    user, error = require_login(request)
    if error:
        return error
    author_id = int(request.path_params.get("author_id"))
    subscription_service.unfollow(user["id"], author_id)
    return HttpResponse.json({"message": "已取消关注"})


def feed(request: HttpRequest) -> HttpResponse:
    user, error = require_login(request)
    if error:
        return error
    items = subscription_service.feed(user["id"], limit=20)
    return HttpResponse.json({"items": items})

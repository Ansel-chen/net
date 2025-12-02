from __future__ import annotations

from server.http_request import HttpRequest
from server.http_response import HttpResponse
from services import post_service

from .utils import require_login


def list_posts(request: HttpRequest) -> HttpResponse:
    limit = int(request.query.get("limit", "20"))
    offset = int(request.query.get("offset", "0"))
    data = post_service.list_posts(limit, offset)
    return HttpResponse.json({"items": data})


def search_posts(request: HttpRequest) -> HttpResponse:
    limit = int(request.query.get("limit", "20"))
    offset = int(request.query.get("offset", "0"))
    keyword = request.query.get("q")
    tag = request.query.get("tag")
    data = post_service.search_posts(keyword, tag, limit, offset)
    return HttpResponse.json({"items": data, "filters": {"q": keyword, "tag": tag}})


def create_post(request: HttpRequest) -> HttpResponse:
    user, error = require_login(request)
    if error:
        return error
    payload = request.json_data or request.form
    if not payload or not payload.get("title"):
        return HttpResponse.json({"error": "标题必填"}, status=400)
    post_id = post_service.create_post(user["id"], payload["title"], payload.get("body", ""), payload.get("tags"))
    return HttpResponse.json({"post_id": post_id}, status=201)


def get_post(request: HttpRequest) -> HttpResponse:
    post_id = int(request.path_params.get("post_id"))
    post = post_service.get_post(post_id)
    if not post:
        return HttpResponse.json({"error": "文章不存在"}, status=404)
    return HttpResponse.json({"post": post})


def update_post(request: HttpRequest) -> HttpResponse:
    user, error = require_login(request)
    if error:
        return error
    payload = request.json_data or request.form
    post_id = int(request.path_params.get("post_id"))
    ok = post_service.update_post(
        post_id,
        user["id"],
        payload.get("title", ""),
        payload.get("body", ""),
        payload.get("tags"),
    )
    if not ok:
        return HttpResponse.json({"error": "无权限或文章不存在"}, status=403)
    return HttpResponse.json({"message": "已更新"})


def delete_post(request: HttpRequest) -> HttpResponse:
    user, error = require_login(request)
    if error:
        return error
    post_id = int(request.path_params.get("post_id"))
    if not post_service.delete_post(post_id, user["id"]):
        return HttpResponse.json({"error": "无权限或文章不存在"}, status=403)
    return HttpResponse.json({"message": "已删除"})


def feed(request: HttpRequest) -> HttpResponse:
    user, error = require_login(request)
    if error:
        return error
    items = post_service.feed_for_user(user["id"], limit=20)
    return HttpResponse.json({"items": items})

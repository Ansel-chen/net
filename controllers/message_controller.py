from __future__ import annotations

from server.http_request import HttpRequest
from server.http_response import HttpResponse
from services import message_service

from .utils import require_login


def send_message(request: HttpRequest) -> HttpResponse:
    user, error = require_login(request)
    if error:
        return error
    payload = request.json_data or request.form
    if not payload:
        return HttpResponse.json({"error": "缺少消息内容"}, status=400)
    receiver_id = int(payload.get("receiver_id", 0))
    subject = payload.get("subject", "")
    body = payload.get("body", "")
    if not receiver_id or not body:
        return HttpResponse.json({"error": "receiver_id 和 body 必填"}, status=400)
    message_id = message_service.send(user["id"], receiver_id, subject, body)
    return HttpResponse.json({"message_id": message_id}, status=201)


def inbox(request: HttpRequest) -> HttpResponse:
    user, error = require_login(request)
    if error:
        return error
    return HttpResponse.json({"items": message_service.inbox(user["id"])})


def outbox(request: HttpRequest) -> HttpResponse:
    user, error = require_login(request)
    if error:
        return error
    return HttpResponse.json({"items": message_service.outbox(user["id"])})

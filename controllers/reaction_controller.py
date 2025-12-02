from __future__ import annotations

from server.http_request import HttpRequest
from server.http_response import HttpResponse
from services import reaction_service

from .utils import require_login


def toggle_reaction(request: HttpRequest) -> HttpResponse:
    user, error = require_login(request)
    if error:
        return error
    payload = request.json_data or request.form
    reaction = payload.get("reaction") if payload else None
    if reaction not in {"like", "favorite"}:
        return HttpResponse.json({"error": "reaction 取值必须是 like 或 favorite"}, status=400)
    post_id = int(request.path_params.get("post_id"))
    stats = reaction_service.toggle(post_id, user["id"], reaction)
    return HttpResponse.json({"stats": stats})

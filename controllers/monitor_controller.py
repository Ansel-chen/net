from __future__ import annotations

from controllers.auth_controller import get_current_user
from server.http_request import HttpRequest
from server.http_response import HttpResponse
from server.template_renderer import render
from server.metrics import metrics_collector


def dashboard(request: HttpRequest) -> HttpResponse:
    user = get_current_user(request)
    metrics = metrics_collector.snapshot()
    html = render(
        "monitor.html",
        {
            "title": "网络性能监测",
            "user": user,
            "metrics": metrics,
        },
    )
    return HttpResponse.text(html)


def network_metrics(request: HttpRequest) -> HttpResponse:
    metrics = metrics_collector.snapshot()
    return HttpResponse.json({"metrics": metrics})

from server.http_request import HttpRequest
from server.http_response import HttpResponse


def home(_: HttpRequest) -> HttpResponse:
    html = """
    <html><head><title>TCP 博客</title></head>
    <body>
    <h1>TCP 博客系统</h1>
    <p>请使用 /api/* 接口与系统交互，可配合 curl 或 Postman 调试。</p>
    </body></html>
    """
    return HttpResponse.text(html)

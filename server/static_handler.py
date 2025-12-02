import mimetypes
import os

import config
from .http_response import HttpResponse


def serve_static(path: str) -> HttpResponse:
    """根据 /static/xxx 的路径返回文件内容"""

    relative_path = path.replace("/static/", "", 1)
    file_path = os.path.join(config.STATIC_ROOT, relative_path)
    if not os.path.isfile(file_path):
        return HttpResponse.text("静态资源未找到", status=404)
    with open(file_path, "rb") as f:
        data = f.read()
    content_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
    headers = {"Content-Type": content_type, "Content-Length": str(len(data))}
    return HttpResponse(status_code=200, reason="OK", headers=headers, body=data)

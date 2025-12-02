from __future__ import annotations

import os
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape

import config

_env = Environment(
    loader=FileSystemLoader(config.TEMPLATE_ROOT),
    autoescape=select_autoescape(["html", "xml"]),
)


def render(template_name: str, context: Dict[str, Any]) -> str:
    """渲染模板"""

    template = _env.get_template(template_name)
    return template.render(**context)

from __future__ import annotations

from controllers.auth_controller import get_current_user
from server.http_request import HttpRequest
from server.http_response import HttpResponse
from server.session import session_store
from server.template_renderer import render
from services import comment_service, post_service


def _render(template: str, context: dict, status: int = 200) -> HttpResponse:
    html = render(template, context)
    return HttpResponse.text(html, status=status)


def home(request: HttpRequest) -> HttpResponse:
    user = get_current_user(request)
    keyword = request.query.get("q")
    tag = request.query.get("tag")
    posts = post_service.search_posts(keyword, tag, limit=20)
    categories = post_service.list_categories(limit=10)
    stats = post_service.get_post_stats()
    latest_post = posts[0] if posts else None
    return _render(
        "home.html",
        {
            "title": "TCP 博客",
            "user": user,
            "posts": posts,
            "keyword": keyword or "",
            "tag": tag or "",
            "categories": categories,
            "post_stats": stats,
            "latest_post": latest_post,
        },
    )


def login_page(request: HttpRequest) -> HttpResponse:
    if get_current_user(request):
        return HttpResponse.redirect("/")
    return _render("login.html", {"title": "登录 - TCP 博客"})


def register_page(request: HttpRequest) -> HttpResponse:
    if get_current_user(request):
        return HttpResponse.redirect("/")
    return _render("register.html", {"title": "注册 - TCP 博客"})


def post_detail(request: HttpRequest) -> HttpResponse:
    post_id = int(request.path_params.get("post_id", 0))
    user = get_current_user(request)
    post = post_service.get_post(post_id, user["id"] if user else None)
    if not post:
        return HttpResponse.text("文章不存在", status=404)
    comments = comment_service.list_comments(post_id)
    return _render(
        "post_detail.html",
        {
            "title": post["title"],
            "post": post,
            "comments": comments,
            "user": user,
        },
    )


def profile_page(request: HttpRequest) -> HttpResponse:
    user = get_current_user(request)
    if not user:
        return HttpResponse.redirect("/login")
    posts = post_service.list_by_author(user["id"], limit=50)
    liked_posts = post_service.list_reacted_posts(user["id"], "like", limit=30)
    favorite_posts = post_service.list_reacted_posts(user["id"], "favorite", limit=30)
    return _render(
        "profile.html",
        {
            "title": "个人主页",
            "user": user,
            "posts": posts,
            "liked_posts": liked_posts,
            "favorite_posts": favorite_posts,
        },
    )


def search_page(request: HttpRequest) -> HttpResponse:
    user = get_current_user(request)
    keyword = (request.query.get("q") or "").strip()
    tag = (request.query.get("tag") or "").strip()
    categories = post_service.list_categories(limit=20)
    has_query = bool(keyword or tag)
    results = (
        post_service.search_posts(keyword or None, tag or None, limit=50)
        if has_query
        else []
    )
    return _render(
        "search.html",
        {
            "title": "搜索文章",
            "user": user,
            "keyword": keyword,
            "tag": tag,
            "results": results,
            "result_count": len(results),
            "categories": categories,
            "has_query": has_query,
            "search_keyword": keyword,
        },
    )


def logout_page(request: HttpRequest) -> HttpResponse:
    session_id = request.cookies.get("session_id")
    if session_id:
        session_store.delete(session_id)
    resp = HttpResponse.redirect("/")
    resp.headers["Set-Cookie"] = "session_id=; Path=/; HttpOnly; Max-Age=0"
    return resp


def new_post_page(request: HttpRequest) -> HttpResponse:
    user = get_current_user(request)
    if not user:
        return HttpResponse.redirect("/login")
    return _render(
        "new_post.html",
        {
            "title": "写文章",
            "user": user,
            "form": {"title": "", "body": "", "tags": ""},
            "error": None,
        },
    )


def submit_post_page(request: HttpRequest) -> HttpResponse:
    user = get_current_user(request)
    if not user:
        return HttpResponse.redirect("/login")
    payload = request.form or request.json_data or {}
    title = (payload.get("title") or "").strip()
    body = (payload.get("body") or "").strip()
    tags = (payload.get("tags") or "").strip()
    form_state = {"title": title, "body": body, "tags": tags}
    if not title:
        return _render(
            "new_post.html",
            {"title": "写文章", "user": user, "form": form_state, "error": "标题不能为空"},
        )
    try:
        post_id = post_service.create_post(user["id"], title, body, tags or None)
    except Exception as exc:
        return _render(
            "new_post.html",
            {
                "title": "写文章",
                "user": user,
                "form": form_state,
                "error": f"创建失败: {exc}",
            },
        )
    return HttpResponse.redirect(f"/posts/{post_id}")

import logging

import config
from controllers import (
    auth_controller,
    comment_controller,
    message_controller,
    monitor_controller,
    page_controller,
    post_controller,
    reaction_controller,
    subscription_controller,
)
from server.router import Router
from server.tcp_http_server import TcpHttpServer

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s %(name)s: %(message)s")


def build_router() -> Router:
    router = Router()

    # 页面与静态展示
    router.add_route("GET", "/", page_controller.home)
    router.add_route("GET", "/login", page_controller.login_page)
    router.add_route("GET", "/register", page_controller.register_page)
    router.add_route("GET", "/logout", page_controller.logout_page)
    router.add_route("GET", "/posts/new", page_controller.new_post_page)
    router.add_route("POST", "/posts/new", page_controller.submit_post_page)
    router.add_route("GET", "/posts/{post_id}", page_controller.post_detail)
    router.add_route("GET", "/profile", page_controller.profile_page)
    router.add_route("GET", "/search", page_controller.search_page)
    router.add_route("GET", "/monitor", monitor_controller.dashboard)

    # 登录注册与会话
    router.add_route("POST", "/api/register", auth_controller.register)
    router.add_route("POST", "/api/login", auth_controller.login)
    router.add_route("POST", "/api/logout", auth_controller.logout)
    router.add_route("GET", "/api/session", auth_controller.current_user)

    # 文章 CRUD
    router.add_route("GET", "/api/posts", post_controller.list_posts)
    router.add_route("GET", "/api/posts/search", post_controller.search_posts)
    router.add_route("POST", "/api/posts", post_controller.create_post)
    router.add_route("GET", "/api/posts/{post_id}", post_controller.get_post)
    router.add_route("POST", "/api/posts/{post_id}/edit", post_controller.update_post)
    router.add_route("POST", "/api/posts/{post_id}/delete", post_controller.delete_post)
    router.add_route("GET", "/api/feed", post_controller.feed)

    # 评论
    router.add_route("GET", "/api/posts/{post_id}/comments", comment_controller.list_comments)
    router.add_route("POST", "/api/posts/{post_id}/comments", comment_controller.add_comment)

    # 点赞收藏
    router.add_route("POST", "/api/posts/{post_id}/reaction", reaction_controller.toggle_reaction)

    # 关注推送
    router.add_route("POST", "/api/authors/{author_id}/follow", subscription_controller.follow_author)
    router.add_route("POST", "/api/authors/{author_id}/unfollow", subscription_controller.unfollow_author)
    router.add_route("GET", "/api/subscriptions/feed", subscription_controller.feed)

    # 私信
    router.add_route("POST", "/api/messages", message_controller.send_message)
    router.add_route("GET", "/api/messages/inbox", message_controller.inbox)
    router.add_route("GET", "/api/messages/outbox", message_controller.outbox)
    router.add_route("GET", "/api/monitor/network", monitor_controller.network_metrics)

    return router


def main() -> None:
    router = build_router()
    server = TcpHttpServer(config.HOST, config.PORT, router)
    server.start()


if __name__ == "__main__":
    main()

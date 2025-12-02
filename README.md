# TCP/HTTP Blog System

## Project Goals

- Implement a browser-server (B/S) blog platform using raw TCP sockets to handle HTTP requests and responses.
- Reinforce understanding of the TCP three-way handshake, HTTP parsing, and application-layer routing without relying on existing web frameworks.
- Provide end-to-end coverage from socket accept loop through backend logic and persistence with MySQL.

## Functional Scope

1. Authentication: user registration, login, logout, session cookie management.
2. Blog content: create/read/update/delete articles, list with pagination, detail view，并提供 `/posts/new` 浏览器表单快速发文。
3. Search & categories: keyword filtering (`q`) and category dropdown (`tag`) exposed via `/api/posts/search` 与首页筛选表单。
4. Profile page: browser route `/profile` 展示个人资料、文章列表，并额外列出“我点赞的文章”“我收藏的文章”历史清单。
5. Mandatory extras:
   - Article comments with nested display.
   - Favorites/likes (one per user per article) plus aggregate counters 以及前端按钮交互，展示个人喜好状态。
   - Article push & subscription: users can follow authors, receive a personalized feed.
   - Private messaging between users (basic inbox/outbox model).
6. Auxiliary pages: HTML home timeline、登录/注册、文章详情、评论交互、网络性能监测面板。

## High-Level Architecture

```
Browser <-> TCP Socket Server <-> Router <-> Controllers <-> Services <-> MySQL
```

- **SocketServer**: Listens on configurable IP/port, manages client sockets, decodes HTTP, spawns worker threads，并把每个请求的延迟/吞吐数据写入 metrics collector。
- **HTTP Parser**: Minimal parser to read request line, headers, optional body (supports `application/json` and `application/x-www-form-urlencoded`).
- **Router**: Maps `(method, path)` to handler functions with simple path parameters (e.g., `/posts/{id}`).
- **Controllers**: Orchestrate request validation, call service layer, and produce `Response` objects.
- **Services**: Encapsulate domain logic (auth, posts, comments, reactions, subscriptions, messaging) and interact with repositories。
- **Repositories/DAO**: Execute parameterized SQL using PyMySQL and return Python objects/dicts。
- **Template Renderer**: Lightweight Jinja2 renderer powering 首页/详情/发文/监控模板。
- **Static File Handler**: Serves CSS/JS/image assets located under `static/` when the router sees `/static/*`。
- **Session Manager**: In-memory dictionary keyed by secure random session IDs persisted via HTTP cookies。
- **Metrics Collector**: `server/metrics.py` 维护 60 秒滑动窗口，供 `/api/monitor/network` 与 `/monitor` 面板实时展示延迟、RTT、吞吐、请求速率等。

## Directory Plan

```
project_root/
├── README.md
├── requirements.txt
├── config.py
├── server/
│   ├── __init__.py
│   ├── tcp_http_server.py
│   ├── http_request.py
│   ├── http_response.py
│   ├── router.py
│   ├── middleware.py
│   ├── templates/
│   └── static/
├── controllers/
│   ├── __init__.py
│   ├── auth_controller.py
│   ├── post_controller.py
│   ├── comment_controller.py
│   ├── reaction_controller.py
│   ├── subscription_controller.py
│   └── message_controller.py
├── services/
│   ├── __init__.py
│   ├── auth_service.py
│   ├── post_service.py
│   ├── comment_service.py
│   ├── reaction_service.py
│   ├── subscription_service.py
│   └── message_service.py
├── repository/
│   ├── __init__.py
│   ├── db.py
│   └── *.py per entity
├── models/
│   ├── __init__.py
│   └── dto.py
├── db/
│   ├── schema.sql
│   └── seed.sql
├── tests/
│   └── integration/
└── tools/
    └── load_test.py
```

## Database Schema (MySQL)

Key indices: unique constraints on `users.username`, `reactions(post_id, user_id, type)`, `subscriptions(follower_id, author_id)`; composite indexes on `posts(author_id, created_at)` to accelerate feed queries.

## HTTP Endpoints (initial set)

- `GET /` 首页列表（含关键词/分类筛选）
- `GET /login`, `GET /register`, `GET /logout` 浏览器页面；`POST /api/login`, `POST /api/register`, `POST /api/logout`, `GET /api/session`
- `GET /posts`, `GET /posts/{id}`（含 `like_count`、`favorite_count`、`liked`、`favorited`）
- `GET /posts/new`, `POST /posts/new` 浏览器表单发文；`POST /api/posts`, `POST /api/posts/{id}/edit`, `POST /api/posts/{id}/delete`
- `POST /api/posts/{id}/comments`, `GET /api/posts/{id}/comments`
- `POST /api/posts/{id}/reaction` 处理点赞/收藏切换
- `POST /api/authors/{id}/follow`, `POST /api/authors/{id}/unfollow`, `GET /api/subscriptions/feed`
- `GET /api/feed` 个性化时间线
- `POST /api/messages`, `GET /api/messages/inbox`, `GET /api/messages/outbox`
- `GET /monitor` 网络性能面板，`GET /api/monitor/network` 返回延迟/RTT/吞吐/请求速率等指标
- `GET /api/posts/search` keyword/category filter for REST or homepage UI

## Browser UI Overview

- **Home (`/`)**: 展示最新文章，支持关键词/分类过滤，并显示每篇文章的点赞/收藏统计。
- **登录/注册 (`/login`, `/register`)**: 调用 API 完成鉴权，成功后写入 `session_id`。
- **发文页 (`/posts/new`)**: 登录用户可通过表单直接创建文章，提交成功自动跳转详情。
- **文章详情 (`/posts/{id}`)**: 展示正文、评论列表与表单，同时提供点赞/收藏按钮，状态与计数实时刷新。
- **个人主页 (`/profile`)**: 展示用户信息、已发布文章及对应点赞/收藏数据，同时分区列出“我点赞过/我收藏过”的文章历史，便于快速回溯内容。
- **监测面板 (`/monitor`)**: 轮询 `/api/monitor/network` 获取最近 60 秒滑动窗口指标，实时可视化延迟、RTT、吞吐量、请求速率和样本数。
- **静态资源**: 所有 CSS 存放于 `server/static`，模板位于 `server/templates` 并由 `template_renderer.py` 渲染。

## Technology Stack

## Next Steps

1. Install dependencies: `pip install -r requirements.txt` (确保已安装 MySQL 并能通过 `config.py` 的 DSN 访问)。
2. 初始化数据库：执行 `db/schema.sql` 创建各数据表；按需插入测试用户与文章数据。
3. 启动服务器：`python main.py`，默认监听 `127.0.0.1:8080`。
4. 浏览器访问 `http://127.0.0.1:8080/`，可使用顶部导航进入登录/注册、发文、监测面板、个人中心等页面，或通过 Postman 调用 `/api/*` 接口进行写操作。
5. 如需 HTTPS，可在 `server/tcp_http_server.py` 中封装 `ssl.wrap_socket` 增强；如需更多前端交互，可以在 `server/templates` 与 `server/static` 目录中扩展模板与样式。

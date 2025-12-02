# TCP/HTTP Blog System

## Project Goals
- Implement a browser-server (B/S) blog platform using raw TCP sockets to handle HTTP requests and responses.
- Reinforce understanding of the TCP three-way handshake, HTTP parsing, and application-layer routing without relying on existing web frameworks.
- Provide end-to-end coverage from socket accept loop through backend logic and persistence with MySQL.

## Functional Scope
1. Authentication: user registration, login, logout, session cookie management.
2. Blog content: create/read/update/delete articles, list with pagination, detail view.
3. Search & categories: keyword filtering (`q`) and category dropdown (`tag`) exposed via `/api/posts/search` 与首页筛选表单。
4. Profile page: browser route `/profile` 展示个人资料、文章列表。
5. Mandatory extras:
   - Article comments with nested display.
   - Favorites/likes (one per user per article) plus aggregate counters.
   - Article push & subscription: users can follow authors, receive a personalized feed.
   - Private messaging between users (basic inbox/outbox model).
6. Auxiliary pages: HTML home timeline、登录/注册、文章详情、评论交互。

## High-Level Architecture
```
Browser <-> TCP Socket Server <-> Router <-> Controllers <-> Services <-> MySQL
```
- **SocketServer**: Listens on configurable IP/port, manages client sockets, decodes HTTP, spawns worker threads.
- **HTTP Parser**: Minimal parser to read request line, headers, optional body (supports `application/json` and `application/x-www-form-urlencoded`).
- **Router**: Maps `(method, path)` to handler functions with simple path parameters (e.g., `/posts/{id}`).
- **Controllers**: Orchestrate request validation, call service layer, and produce `Response` objects.
- **Services**: Encapsulate domain logic (auth, posts, comments, reactions, subscriptions, messaging) and interact with repositories.
- **Repositories/DAO**: Execute parameterized SQL using PyMySQL and return Python objects/dicts.
- **Template Renderer**: Lightweight Jinja2-inspired renderer for HTML pages (or fallback to string formatting if templating library unavailable).
- **Static File Handler**: Serves CSS/JS/image assets located under `static/` when the router sees `/static/*`.
- **Session Manager**: In-memory dictionary keyed by secure random session IDs persisted via HTTP cookies.

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
- `users(id, username, password_hash, salt, nickname, email, bio, created_at)`
- `sessions(id, user_id, expires_at, created_at)` (mirror in memory for fast lookup)
- `posts(id, author_id, title, body, tags, is_public, created_at, updated_at)`
- `comments(id, post_id, user_id, parent_id NULL, body, created_at)`
- `reactions(id, post_id, user_id, type ENUM('like','favorite'), created_at)`
- `subscriptions(id, follower_id, author_id, created_at)`
- `messages(id, sender_id, receiver_id, subject, body, is_read, created_at)`
- `notifications(id, user_id, payload_json, is_read, created_at)` for push/subscription feed caching.

Key indices: unique constraints on `users.username`, `reactions(post_id, user_id, type)`, `subscriptions(follower_id, author_id)`; composite indexes on `posts(author_id, created_at)` to accelerate feed queries.

## HTTP Endpoints (initial set)
- `GET /` home timeline (if logged in show followed authors; else popular posts)
- `GET /login`, `GET /register`, `GET /logout` browser pages with fetch-based auth forms
- `GET /posts/{id}` article detail page + inline comment submission
- `GET /profile` personal dashboard (requires login)
- `GET /login`, `POST /login`, `GET /register`, `POST /register`, `POST /logout`
- `GET /posts`, `GET /posts/{id}`
- `POST /posts`, `POST /posts/{id}/edit`, `POST /posts/{id}/delete`
- `POST /posts/{id}/comments`, `GET /posts/{id}/comments`
- `POST /posts/{id}/reaction` (body chooses like/favorite)
- `POST /authors/{id}/subscribe`, `POST /authors/{id}/unsubscribe`
- `GET /feed` personalized feed
- `GET /messages`, `GET /messages/new`, `POST /messages`, `GET /messages/{id}`
- `GET /api/posts/search` keyword/category filter for REST or homepage UI

## Browser UI Overview
- **Home (`/`)**: 展示最新文章，支持关键词与分类联动搜索，下方列表链接到详情页。
- **登录/注册 (`/login`, `/register`)**: 纯前端表单，调用 `/api/login`、`/api/register` 完成鉴权，成功后写入 `session_id` cookie。
- **文章详情 (`/posts/{id}`)**: 渲染正文与评论，并允许已登录用户通过 fetch 调用 `/api/posts/{id}/comments` 发表评论。
- **个人主页 (`/profile`)**: 登录后显示用户个人信息、文章列表，可配合 API 做编辑或删除。
- **静态资源**: 所有 CSS 放在 `server/static`，模板位于 `server/templates` 并由 `server/template_renderer.py` 的 Jinja 环境加载。

## Technology Stack
- Python 3.10+ running inside `conda` environment `net`.
- Standard library: `socket`, `threading`, `logging`, `ssl` (optional for HTTPS extension), `uuid`, `hashlib`, `hmac`, `datetime`, `json`.
- Third-party: `PyMySQL` (DB driver), `bcrypt` (password hashing) or fallback to `hashlib.pbkdf2_hmac` if installation becomes an issue.
- MySQL 8.x server accessible via configurable DSN from `.env` or config settings.

## Next Steps
1. Install dependencies: `pip install -r requirements.txt` (确保已安装 MySQL 并能通过 `config.py` 的 DSN 访问)。
2. 初始化数据库：执行 `db/schema.sql` 创建各数据表；按需插入测试用户与文章数据。
3. 启动服务器：`python main.py`，默认监听 `127.0.0.1:8080`。
4. 浏览器访问 `http://127.0.0.1:8080/`，可使用顶部导航进入登录/注册、个人中心等页面，或通过 Postman 调用 `/api/*` 接口进行写操作。
5. 如需 HTTPS，可在 `server/tcp_http_server.py` 中封装 `ssl.wrap_socket` 增强；如需更多前端交互，可以在 `server/templates` 与 `server/static` 目录中扩展模板与样式。

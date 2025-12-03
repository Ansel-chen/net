# TCP/HTTP 博客系统

## 项目目标

- 使用原生 TCP 套接字（Socket）实现一个浏览器-服务器（B/S）架构的博客平台，手动处理 HTTP 请求与响应。
- 在不依赖现有 Web 框架（如 Flask/Django）的情况下，加深对 TCP 三次握手、HTTP 协议解析和应用层路由的理解。
- 提供从 Socket `accept` 循环开始，贯穿后端逻辑，直到 MySQL 数据持久化的端到端完整实现。

## 功能范围

1.  **用户认证**：支持用户注册、登录、注销以及 Session Cookie 管理。
2.  **博客内容**：支持文章的创建/读取/更新/删除 (CRUD)，分页显示列表，详情视图，并提供 `/posts/new` 浏览器表单用于快速发文。
3.  **搜索与分类**：通过 `/api/posts/search` 接口、首页筛选表单以及全局 `/search` 页面，提供关键词 (`q`) 与分类 (`tag`) 组合过滤。
4.  **个人主页**：浏览器路由 `/profile` 展示个人资料、发布的文章列表，并额外列出“我点赞的文章”和“我收藏的文章”历史清单。
5.  **核心扩展功能**：
    - 文章评论（支持嵌套显示）。
    - 收藏/点赞（每位用户每篇文章限一次），包含聚合计数以及前端按钮交互，实时展示个人喜好状态。
    - 文章推送与订阅：用户可以关注作者，接收个性化的 Feed 流。
    - 用户私信（基础的收件箱/发件箱模型）。
6.  **辅助页面**：HTML 首页时间线、登录/注册页、文章详情页、评论交互区域、网络性能监测面板。

## 高层架构

```
Browser <-> TCP Socket Server <-> Router <-> Controllers <-> Services <-> MySQL
```

- **SocketServer**: 监听可配置的 IP/端口，管理客户端 Socket 连接，解码 HTTP 协议，生成工作线程，并将每个请求的延迟/吞吐数据写入指标收集器 (Metrics Collector)。
- **HTTP Parser**: 极简解析器，负责读取请求行、头部信息、可选包体（支持 `application/json` 和 `application/x-www-form-urlencoded`）。
- **Router**: 将 `(method, path)` 映射到对应的处理函数，支持简单的路径参数（例如 `/posts/{id}`）。
- **Controllers**: 编排请求验证，调用服务层 (Service Layer)，并生成 `Response` 对象。
- **Services**: 封装领域逻辑（认证、文章、评论、互动、订阅、消息）并与数据仓库 (Repositories) 交互。
- **Repositories/DAO**: 使用 PyMySQL 执行参数化 SQL 语句，并返回 Python 对象/字典。
- **Template Renderer**: 轻量级 Jinja2 渲染器，用于渲染首页、详情页、发文页和监控面板等模板。
- **Static File Handler**: 当路由器匹配到 `/static/*` 路径时，提供位于 `static/` 目录下的 CSS/JS/图片资源。
- **Session Manager**: 基于内存的字典，以安全随机生成的 Session ID 为键，并通过 HTTP Cookie 进行持久化。
- **Metrics Collector**: `server/metrics.py` 维护 60 秒滑动窗口，供 `/api/monitor/network` 接口与 `/monitor` 面板实时展示延迟、RTT、吞吐量、请求速率等指标。

## 目录规划

```
project_root/
├── README.md
├── requirements.txt
├── config.py
├── server/
│   ├── __init__.py
│   ├── tcp_http_server.py
│   ├── http_request.py
│   ├── http_response.py
│   ├── router.py
│   ├── middleware.py
│   ├── templates/
│   └── static/
├── controllers/
│   ├── __init__.py
│   ├── auth_controller.py
│   ├── post_controller.py
│   ├── comment_controller.py
│   ├── reaction_controller.py
│   ├── subscription_controller.py
│   └── message_controller.py
├── services/
│   ├── __init__.py
│   ├── auth_service.py
│   ├── post_service.py
│   ├── comment_service.py
│   ├── reaction_service.py
│   ├── subscription_service.py
│   └── message_service.py
├── repository/
│   ├── __init__.py
│   ├── db.py
│   └── *.py (每个实体对应的仓库文件)
├── models/
│   ├── __init__.py
│   └── dto.py
├── db/
│   ├── schema.sql
│   └── seed.sql
├── tests/
│   └── integration/
└── tools/
    └── load_test.py
```

## 数据库 Schema (MySQL)

关键索引设计：

- 唯一约束：`users.username`，`reactions(post_id, user_id, type)`，`subscriptions(follower_id, author_id)`。
- 复合索引：`posts(author_id, created_at)` 用于加速 Feed 流查询。

## HTTP 端点 (初始集合)

- `GET /` 首页列表（含关键词/分类筛选）
- `GET /login`, `GET /register`, `GET /logout` 浏览器页面；`POST /api/login`, `POST /api/register`, `POST /api/logout`, `GET /api/session`
- `GET /posts`, `GET /posts/{id}`（返回包含 `like_count`、`favorite_count`、`liked`、`favorited` 等字段）
- `GET /posts/new`, `POST /posts/new` 浏览器发文表单；`POST /api/posts`, `POST /api/posts/{id}/edit`, `POST /api/posts/{id}/delete`
- `POST /api/posts/{id}/comments`, `GET /api/posts/{id}/comments`
- `POST /api/posts/{id}/reaction` 处理点赞/收藏状态切换
- `POST /api/authors/{id}/follow`, `POST /api/authors/{id}/unfollow`, `GET /api/subscriptions/feed`
- `GET /api/feed` 个性化时间线
- `POST /api/messages`, `GET /api/messages/inbox`, `GET /api/messages/outbox`
- `GET /monitor` 网络性能面板，`GET /api/monitor/network` 返回延迟/RTT/吞吐/请求速率等指标
- `GET /api/posts/search` 支持关键词/分类过滤（供 REST API 或首页 UI 使用）

## 浏览器 UI 概览

- **首页 (`/`)**: 展示最新文章，支持关键词/分类过滤，并显示每篇文章的点赞/收藏统计。
- **全局搜索 (`/search`)**: 导航栏随处可用的搜索表单，支持关键字/标签组合检索文章并以卡片方式展示结果统计。
- **登录/注册 (`/login`, `/register`)**: 调用 API 完成鉴权，成功后写入 `session_id`。
- **发文页 (`/posts/new`)**: 登录用户可通过表单直接创建文章，提交成功自动跳转详情。
- **文章详情 (`/posts/{id}`)**: 展示正文、评论列表与表单，同时提供点赞/收藏按钮，状态与计数实时刷新。
- **个人主页 (`/profile`)**: 展示用户信息、已发布文章及对应点赞/收藏数据，同时分区列出“我点赞过/我收藏过”的文章历史，便于快速回溯内容。
- **监测面板 (`/monitor`)**: 轮询 `/api/monitor/network` 获取最近 60 秒滑动窗口指标，实时可视化延迟、RTT、吞吐量、请求速率和样本数。
- **静态资源**: 所有 CSS 存放于 `server/static`，模板位于 `server/templates` 并由 `template_renderer.py` 渲染。

## 技术栈

_(此处原文档为空，通常隐含 Python + MySQL)_

## 下一步计划

1.  **安装依赖**: `pip install -r requirements.txt` (确保已安装 MySQL 并能通过 `config.py` 的 DSN 访问)。
2.  **初始化数据库**: 执行 `db/schema.sql` 创建各数据表；按需插入测试用户与文章数据。
3.  **启动服务器**: `python main.py`，默认监听 `127.0.0.1:8080`。
4.  **访问验证**: 浏览器访问 `http://127.0.0.1:8080/`，可使用顶部导航进入登录/注册、发文、监测面板、个人中心等页面，或通过 Postman 调用 `/api/*` 接口进行写操作。
5.  **扩展建议**: 如需 HTTPS，可在 `server/tcp_http_server.py` 中封装 `ssl.wrap_socket` 增强；如需更多前端交互，可以在 `server/templates` 与 `server/static` 目录中扩展模板与样式。

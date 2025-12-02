# TCP/HTTP Blog System

## Project Goals
- Implement a browser-server (B/S) blog platform using raw TCP sockets to handle HTTP requests and responses.
- Reinforce understanding of the TCP three-way handshake, HTTP parsing, and application-layer routing without relying on existing web frameworks.
- Provide end-to-end coverage from socket accept loop through backend logic and persistence with MySQL.

## Functional Scope
1. Authentication: user registration, login, logout, session cookie management.
2. Blog content: create/read/update/delete articles, list with pagination, detail view.
3. Mandatory extras:
   - Article comments with nested display.
   - Favorites/likes (one per user per article) plus aggregate counters.
   - Article push & subscription: users can follow authors, receive a personalized feed.
   - Private messaging between users (basic inbox/outbox model).
4. Auxiliary pages: profile view, search/filter by tag/category, home timeline.

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
- `GET /login`, `POST /login`, `GET /register`, `POST /register`, `POST /logout`
- `GET /posts`, `GET /posts/{id}`
- `POST /posts`, `POST /posts/{id}/edit`, `POST /posts/{id}/delete`
- `POST /posts/{id}/comments`, `GET /posts/{id}/comments`
- `POST /posts/{id}/reaction` (body chooses like/favorite)
- `POST /authors/{id}/subscribe`, `POST /authors/{id}/unsubscribe`
- `GET /feed` personalized feed
- `GET /messages`, `GET /messages/new`, `POST /messages`, `GET /messages/{id}`

## Technology Stack
- Python 3.10+ running inside `conda` environment `net`.
- Standard library: `socket`, `threading`, `logging`, `ssl` (optional for HTTPS extension), `uuid`, `hashlib`, `hmac`, `datetime`, `json`.
- Third-party: `PyMySQL` (DB driver), `bcrypt` (password hashing) or fallback to `hashlib.pbkdf2_hmac` if installation becomes an issue.
- MySQL 8.x server accessible via configurable DSN from `.env` or config settings.

## Next Steps
1. Create `requirements.txt`, `config.py`, and code directories as outlined.
2. Author `db/schema.sql` with full table creation statements and helpful indexes.
3. Implement socket server core (`tcp_http_server.py`) and request/response helpers.
4. Incrementally build controllers/services, wiring them to MySQL using the repository layer.
5. Provide HTML templates and static assets; ensure responses include correct HTTP headers.
6. Write integration tests/scripts that run HTTP requests via `socket` or `requests` for verification.

import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

HOST = os.environ.get("BLOG_HOST", "127.0.0.1")
PORT = int(os.environ.get("BLOG_PORT", "8080"))

DB_CONFIG = {
    "host": os.environ.get("BLOG_DB_HOST", "127.0.0.1"),
    "port": int(os.environ.get("BLOG_DB_PORT", "3306")),
    "user": os.environ.get("BLOG_DB_USER", "root"),
    "password": os.environ.get("BLOG_DB_PASSWORD", "root"),
    "database": os.environ.get("BLOG_DB_NAME", "tcp_blog"),
    "charset": "utf8mb4",
    "cursorclass": None,
}

SECRET_KEY = os.environ.get("BLOG_SECRET_KEY", "dev-secret-key")
SESSION_EXPIRE_SECONDS = int(os.environ.get("BLOG_SESSION_EXPIRE", "86400"))
MAX_REQUEST_SIZE = int(os.environ.get("BLOG_MAX_REQ", "1048576"))
STATIC_ROOT = os.path.join(BASE_DIR, "server", "static")
TEMPLATE_ROOT = os.path.join(BASE_DIR, "server", "templates")

import bcrypt

from repository import user_repo
from server.session import session_store


def register(username: str, password: str, nickname: str, email: str | None) -> int:
    """注册新用户"""

    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
    return user_repo.create_user(username, password_hash, salt.decode("utf-8"), nickname, email)


def login(username: str, password: str) -> str | None:
    """校验账号密码并创建会话"""

    user = user_repo.find_by_username(username)
    if not user:
        return None
    stored_hash = user["password_hash"].encode("utf-8")
    if bcrypt.checkpw(password.encode("utf-8"), stored_hash):
        return session_store.create(user["id"])
    return None


def get_user(user_id: int):
    return user_repo.find_by_id(user_id)

from __future__ import annotations

from typing import Dict, Optional

from .db import get_cursor


def create_user(username: str, password_hash: str, salt: str, nickname: str, email: str | None) -> int:
    """插入新用户"""

    with get_cursor() as cursor:
        sql = """
        INSERT INTO users (username, password_hash, salt, nickname, email)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (username, password_hash, salt, nickname, email))
        return cursor.lastrowid


def find_by_username(username: str) -> Optional[Dict]:
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        return cursor.fetchone()


def find_by_id(user_id: int) -> Optional[Dict]:
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
        return cursor.fetchone()

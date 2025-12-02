from __future__ import annotations

from typing import Dict, List, Optional

from .db import get_cursor


def create_post(author_id: int, title: str, body: str, tags: str | None) -> int:
    with get_cursor() as cursor:
        sql = "INSERT INTO posts (author_id, title, body, tags) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (author_id, title, body, tags))
        return cursor.lastrowid


def list_posts(limit: int = 20, offset: int = 0) -> List[Dict]:
    with get_cursor() as cursor:
        cursor.execute(
            "SELECT posts.*, users.nickname AS author_name FROM posts JOIN users ON posts.author_id=users.id ORDER BY created_at DESC LIMIT %s OFFSET %s",
            (limit, offset),
        )
        return cursor.fetchall()


def list_by_author(author_id: int, limit: int = 20) -> List[Dict]:
    with get_cursor() as cursor:
        cursor.execute(
            "SELECT * FROM posts WHERE author_id=%s ORDER BY created_at DESC LIMIT %s",
            (author_id, limit),
        )
        return cursor.fetchall()


def get_post(post_id: int) -> Optional[Dict]:
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM posts WHERE id=%s", (post_id,))
        return cursor.fetchone()


def delete_post(post_id: int, author_id: int) -> bool:
    with get_cursor() as cursor:
        rows = cursor.execute("DELETE FROM posts WHERE id=%s AND author_id=%s", (post_id, author_id))
        return rows > 0


def update_post(post_id: int, author_id: int, title: str, body: str, tags: str | None) -> bool:
    with get_cursor() as cursor:
        sql = "UPDATE posts SET title=%s, body=%s, tags=%s WHERE id=%s AND author_id=%s"
        rows = cursor.execute(sql, (title, body, tags, post_id, author_id))
        return rows > 0

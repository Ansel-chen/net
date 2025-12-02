from __future__ import annotations

from typing import Dict, List

from .db import get_cursor


def create_comment(post_id: int, user_id: int, body: str, parent_id: int | None) -> int:
    with get_cursor() as cursor:
        sql = "INSERT INTO comments (post_id, user_id, body, parent_id) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (post_id, user_id, body, parent_id))
        return cursor.lastrowid


def list_by_post(post_id: int) -> List[Dict]:
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT comments.*, users.nickname AS author_name
            FROM comments JOIN users ON comments.user_id = users.id
            WHERE comments.post_id=%s ORDER BY comments.created_at ASC
            """,
            (post_id,),
        )
        return cursor.fetchall()

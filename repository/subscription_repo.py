from __future__ import annotations

from typing import Dict, List

from .db import get_cursor


def follow(follower_id: int, author_id: int) -> None:
    with get_cursor() as cursor:
        cursor.execute(
            "INSERT IGNORE INTO subscriptions (follower_id, author_id) VALUES (%s, %s)",
            (follower_id, author_id),
        )


def unfollow(follower_id: int, author_id: int) -> None:
    with get_cursor() as cursor:
        cursor.execute("DELETE FROM subscriptions WHERE follower_id=%s AND author_id=%s", (follower_id, author_id))


def list_feed(user_id: int, limit: int = 20) -> List[Dict]:
    """列出关注作者的最新文章"""

    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT posts.*, users.nickname AS author_name
            FROM posts
            JOIN subscriptions ON posts.author_id = subscriptions.author_id
            JOIN users ON users.id = posts.author_id
            LEFT JOIN (
                SELECT post_id,
                       SUM(CASE WHEN reaction_type = 'like' THEN 1 ELSE 0 END) AS like_count,
                       SUM(CASE WHEN reaction_type = 'favorite' THEN 1 ELSE 0 END) AS favorite_count
                FROM reactions
                GROUP BY post_id
            ) AS react ON react.post_id = posts.id
            WHERE subscriptions.follower_id=%s
            ORDER BY posts.created_at DESC LIMIT %s
            """,
            (user_id, limit),
        )
        return cursor.fetchall()

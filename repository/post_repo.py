from __future__ import annotations

from typing import Dict, List, Optional

from .db import get_cursor

REACTION_JOIN = """
    LEFT JOIN (
        SELECT post_id,
               SUM(CASE WHEN reaction_type = 'like' THEN 1 ELSE 0 END) AS like_count,
               SUM(CASE WHEN reaction_type = 'favorite' THEN 1 ELSE 0 END) AS favorite_count
        FROM reactions
        GROUP BY post_id
    ) AS react ON react.post_id = posts.id
"""


def create_post(author_id: int, title: str, body: str, tags: str | None) -> int:
    with get_cursor() as cursor:
        sql = "INSERT INTO posts (author_id, title, body, tags) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (author_id, title, body, tags))
        return cursor.lastrowid


def list_posts(limit: int = 20, offset: int = 0) -> List[Dict]:
    with get_cursor() as cursor:
        cursor.execute(
            f"""
            SELECT posts.*, users.nickname AS author_name,
                   COALESCE(react.like_count, 0) AS like_count,
                   COALESCE(react.favorite_count, 0) AS favorite_count
            FROM posts
            JOIN users ON posts.author_id = users.id
            {REACTION_JOIN}
            ORDER BY posts.created_at DESC
            LIMIT %s OFFSET %s
            """,
            (limit, offset),
        )
        return cursor.fetchall()


def list_by_author(author_id: int, limit: int = 20) -> List[Dict]:
    with get_cursor() as cursor:
        cursor.execute(
            f"""
            SELECT posts.*,
                   COALESCE(react.like_count, 0) AS like_count,
                   COALESCE(react.favorite_count, 0) AS favorite_count
            FROM posts
            {REACTION_JOIN}
            WHERE posts.author_id = %s
            ORDER BY posts.created_at DESC
            LIMIT %s
            """,
            (author_id, limit),
        )
        return cursor.fetchall()


def search_posts(keyword: str | None, tag: str | None, limit: int = 20, offset: int = 0) -> List[Dict]:
    with get_cursor() as cursor:
        sql = [
            """
            SELECT posts.*, users.nickname AS author_name,
                   COALESCE(react.like_count, 0) AS like_count,
                   COALESCE(react.favorite_count, 0) AS favorite_count
            FROM posts
            JOIN users ON posts.author_id = users.id
            """,
            REACTION_JOIN,
        ]
        conditions = []
        params: list = []
        if keyword:
            like = f"%{keyword}%"
            conditions.append("(posts.title LIKE %s OR posts.body LIKE %s)")
            params.extend([like, like])
        if tag:
            conditions.append("posts.tags = %s")
            params.append(tag)
        if conditions:
            sql.append("WHERE " + " AND ".join(conditions))
        sql.append("ORDER BY posts.created_at DESC LIMIT %s OFFSET %s")
        params.extend([limit, offset])
        cursor.execute(" ".join(sql), params)
        return cursor.fetchall()


def list_categories(limit: int = 10) -> List[Dict]:
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT tags AS category, COUNT(*) AS count
            FROM posts
            WHERE tags IS NOT NULL AND tags <> ''
            GROUP BY tags
            ORDER BY count DESC
            LIMIT %s
            """,
            (limit,),
        )
        return cursor.fetchall()


def get_post(post_id: int) -> Optional[Dict]:
    with get_cursor() as cursor:
        cursor.execute(
            f"""
            SELECT posts.*, users.nickname AS author_name,
                   COALESCE(react.like_count, 0) AS like_count,
                   COALESCE(react.favorite_count, 0) AS favorite_count
            FROM posts
            JOIN users ON posts.author_id = users.id
            {REACTION_JOIN}
            WHERE posts.id = %s
            """,
            (post_id,),
        )
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


def list_reacted_by_user(user_id: int, reaction_type: str, limit: int = 20) -> List[Dict]:
    with get_cursor() as cursor:
        cursor.execute(
            f"""
            SELECT posts.*, users.nickname AS author_name,
                   COALESCE(react.like_count, 0) AS like_count,
                   COALESCE(react.favorite_count, 0) AS favorite_count,
                   reacts.created_at AS reacted_at
            FROM reactions AS reacts
            JOIN posts ON reacts.post_id = posts.id
            JOIN users ON posts.author_id = users.id
            {REACTION_JOIN}
            WHERE reacts.user_id = %s AND reacts.reaction_type = %s
            ORDER BY reacts.created_at DESC
            LIMIT %s
            """,
            (user_id, reaction_type, limit),
        )
        return cursor.fetchall()

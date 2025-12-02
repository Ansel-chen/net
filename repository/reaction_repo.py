from __future__ import annotations

from typing import Dict

from .db import get_cursor


def toggle_reaction(post_id: int, user_id: int, reaction_type: str) -> Dict[str, int]:
    """点赞或收藏，若已存在则删除"""

    with get_cursor() as cursor:
        cursor.execute(
            "DELETE FROM reactions WHERE post_id=%s AND user_id=%s AND reaction_type=%s",
            (post_id, user_id, reaction_type),
        )
        if cursor.rowcount == 0:
            cursor.execute(
                "INSERT INTO reactions (post_id, user_id, reaction_type) VALUES (%s, %s, %s)",
                (post_id, user_id, reaction_type),
            )
        cursor.execute(
            "SELECT reaction_type, COUNT(*) AS cnt FROM reactions WHERE post_id=%s GROUP BY reaction_type",
            (post_id,),
        )
        stats = {row["reaction_type"]: row["cnt"] for row in cursor.fetchall()}
        return {"like": stats.get("like", 0), "favorite": stats.get("favorite", 0)}

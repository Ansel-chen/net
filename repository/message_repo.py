from __future__ import annotations

from typing import Dict, List

from .db import get_cursor


def send_message(sender_id: int, receiver_id: int, subject: str, body: str) -> int:
    with get_cursor() as cursor:
        cursor.execute(
            "INSERT INTO messages (sender_id, receiver_id, subject, body) VALUES (%s, %s, %s, %s)",
            (sender_id, receiver_id, subject, body),
        )
        return cursor.lastrowid


def list_inbox(user_id: int) -> List[Dict]:
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT messages.*, u.nickname AS sender_name
            FROM messages JOIN users u ON messages.sender_id = u.id
            WHERE receiver_id=%s ORDER BY created_at DESC
            """,
            (user_id,),
        )
        return cursor.fetchall()


def list_outbox(user_id: int) -> List[Dict]:
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT messages.*, u.nickname AS receiver_name
            FROM messages JOIN users u ON messages.receiver_id = u.id
            WHERE sender_id=%s ORDER BY created_at DESC
            """,
            (user_id,),
        )
        return cursor.fetchall()

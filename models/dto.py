from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    id: int
    username: str
    nickname: str
    email: Optional[str]
    bio: Optional[str]
    created_at: datetime


@dataclass
class Post:
    id: int
    author_id: int
    title: str
    body: str
    tags: Optional[str]
    is_public: bool
    created_at: datetime
    updated_at: datetime


@dataclass
class Comment:
    id: int
    post_id: int
    user_id: int
    parent_id: Optional[int]
    body: str
    created_at: datetime


@dataclass
class Message:
    id: int
    sender_id: int
    receiver_id: int
    subject: str
    body: str
    is_read: bool
    created_at: datetime

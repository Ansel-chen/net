from __future__ import annotations

import contextlib
from typing import Generator

import pymysql

import config


def get_connection():
    """创建数据库连接"""

    return pymysql.connect(
        host=config.DB_CONFIG["host"],
        port=config.DB_CONFIG["port"],
        user=config.DB_CONFIG["user"],
        password=config.DB_CONFIG["password"],
        database=config.DB_CONFIG["database"],
        charset=config.DB_CONFIG["charset"],
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


@contextlib.contextmanager
def get_cursor() -> Generator[pymysql.cursors.Cursor, None, None]:
    """上下文管理游标"""

    conn = get_connection()
    cursor = conn.cursor()
    try:
        yield cursor
    finally:
        cursor.close()
        conn.close()

import sqlite3
from app.core.config import settings


def get_connection():
    connection = sqlite3.connect(settings.DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def fetch_all(query: str, params: tuple = ()):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    connection.close()
    return [dict(row) for row in rows]


def fetch_one(query: str, params: tuple = ()):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(query, params)
    row = cursor.fetchone()
    connection.close()
    return dict(row) if row else None


def execute_query(query: str, params: tuple = ()):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(query, params)
    connection.commit()
    last_id = cursor.lastrowid
    connection.close()
    return last_id


def get_table_columns(table_name: str):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    rows = cursor.fetchall()
    connection.close()
    return [row["name"] for row in rows]
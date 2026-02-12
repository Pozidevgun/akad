"""
Модуль для роботи з SQLite базою даних маркетингової аналітики.
"""
import sqlite3
from pathlib import Path
from contextlib import contextmanager


# Шлях до БД відносно кореня проекту
DB_PATH = Path(__file__).parent.parent / "data" / "marketing.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


@contextmanager
def get_connection():
    """Контекстний менеджер для підключення до БД."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Результати як словники
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_database():
    """Ініціалізація БД — створення таблиць з schema.sql."""
    with get_connection() as conn:
        schema = SCHEMA_PATH.read_text(encoding="utf-8")
        conn.executescript(schema)
    print(f"✓ База даних ініціалізована: {DB_PATH}")


def execute_query(sql: str, params: tuple = ()):
    """Виконати SELECT і повернути результат."""
    with get_connection() as conn:
        cursor = conn.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]


def execute_many(table: str, columns: list, rows: list[dict], conflict: str = "REPLACE"):
    """Масове вставлення з ON CONFLICT REPLACE (upsert).
    rows — список словників, keys мають збігатися з columns.
    """
    if not rows:
        return 0
    placeholders = ", ".join(["?" for _ in columns])
    cols = ", ".join(columns)
    sql = f"INSERT OR {conflict} INTO {table} ({cols}) VALUES ({placeholders})"
    # Конвертувати dict -> tuple у правильному порядку
    tuples = [tuple(r.get(c) for c in columns) for r in rows]
    with get_connection() as conn:
        cursor = conn.executemany(sql, tuples)
        return cursor.rowcount

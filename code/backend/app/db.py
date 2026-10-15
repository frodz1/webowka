import time
from pathlib import Path

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from . import config

_pool = None
SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schema.sql"


def get_pool():
    global _pool
    if _pool is None:
        _pool = ConnectionPool(
            config.DATABASE_URL,
            min_size=1,
            max_size=10,
            kwargs={"row_factory": dict_row},
            open=True,
        )
    return _pool


def query(sql, params=None):
    """Zwraca listę wierszy (dict). Transakcja jest zatwierdzana po wykonaniu."""
    with get_pool().connection() as conn:
        cur = conn.execute(sql, params)
        return cur.fetchall() if cur.description else []


def query_one(sql, params=None):
    rows = query(sql, params)
    return rows[0] if rows else None


def init_schema(retries=30, delay=1.0):
    """Czeka na bazę i tworzy tabele (idempotentnie)."""
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    last_error = None
    for _ in range(retries):
        try:
            with psycopg.connect(config.DATABASE_URL, autocommit=True) as conn:
                conn.execute(sql)
            return
        except psycopg.OperationalError as exc:
            last_error = exc
            time.sleep(delay)
    raise RuntimeError(f"Baza danych niedostępna: {last_error}")

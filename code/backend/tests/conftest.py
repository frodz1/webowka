import itertools
import os

import psycopg
from psycopg import sql
import pytest
from psycopg.conninfo import conninfo_to_dict, make_conninfo

from app import config

# Testy używają osobnej bazy, żeby nie czyścić danych deweloperskich.
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")
if TEST_DATABASE_URL:
    config.DATABASE_URL = TEST_DATABASE_URL

from app import create_app  # noqa: E402
from app.db import get_pool, init_schema  # noqa: E402

_counter = itertools.count(1)


def _ensure_test_database():
    params = conninfo_to_dict(config.DATABASE_URL)
    name = params["dbname"]
    admin = make_conninfo(config.DATABASE_URL, dbname="postgres")
    with psycopg.connect(admin, autocommit=True) as conn:
        exists = conn.execute("SELECT 1 FROM pg_database WHERE datname = %s", (name,)).fetchone()
        if not exists:
            conn.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))


@pytest.fixture(scope="session", autouse=True)
def _schema():
    if TEST_DATABASE_URL:
        _ensure_test_database()
    init_schema()


@pytest.fixture(autouse=True)
def _clean_db(_schema):
    with get_pool().connection() as conn:
        conn.execute("TRUNCATE votes, comments, posts, users RESTART IDENTITY CASCADE")
    yield


@pytest.fixture
def client():
    return create_app().test_client()


@pytest.fixture
def register(client):
    """Zakłada użytkownika i zwraca (nagłówki z tokenem, dane użytkownika)."""

    def _register(username=None, password="sekret123"):
        n = next(_counter)
        username = username or f"user{n}"
        res = client.post(
            "/api/auth/register",
            json={"username": username, "email": f"{username}@example.com", "password": password},
        )
        assert res.status_code == 201, res.get_json()
        body = res.get_json()
        return {"Authorization": f"Bearer {body['token']}"}, body["user"]

    return _register

import pytest

from app import config, create_app
from app.db import query_one
from app.extensions import limiter

PASSWORD = "sekretne-haslo-1"


def register_user(client, name="anna"):
    return client.post(
        "/api/auth/register",
        json={"username": name, "email": f"{name}@example.com", "password": PASSWORD},
    )


def login(client, password, name="anna"):
    return client.post("/api/auth/login", json={"login": name, "password": password})


def test_password_length_bounds(client):
    short = client.post("/api/auth/register", json={"username": "bob", "email": "b@y.pl", "password": "123456789"})
    assert short.status_code == 400
    long = client.post("/api/auth/register", json={"username": "bob", "email": "b@y.pl", "password": "x" * 129})
    assert long.status_code == 400
    ok = client.post("/api/auth/register", json={"username": "bob", "email": "b@y.pl", "password": "x" * 128})
    assert ok.status_code == 201


def test_account_locks_after_failed_logins(client):
    register_user(client)
    for _ in range(config.LOGIN_MAX_ATTEMPTS):
        assert login(client, "zle-haslo").status_code == 401
    assert login(client, "zle-haslo").status_code == 429
    assert login(client, PASSWORD).status_code == 429


def test_lock_expires_and_counter_resets(client):
    register_user(client)
    for _ in range(config.LOGIN_MAX_ATTEMPTS):
        login(client, "zle-haslo")
    query_one("UPDATE users SET locked_until = now() - interval '1 minute' RETURNING id")
    assert login(client, PASSWORD).status_code == 200
    row = query_one("SELECT failed_logins, locked_until FROM users")
    assert row["failed_logins"] == 0 and row["locked_until"] is None


def test_successful_login_resets_failed_counter(client):
    register_user(client)
    for _ in range(config.LOGIN_MAX_ATTEMPTS - 1):
        login(client, "zle-haslo")
    assert login(client, PASSWORD).status_code == 200
    for _ in range(config.LOGIN_MAX_ATTEMPTS - 1):
        assert login(client, "zle-haslo").status_code == 401


def test_unknown_user_gets_same_response_as_wrong_password(client):
    register_user(client)
    missing = login(client, PASSWORD, name="nikt")
    wrong = login(client, "zle-haslo")
    assert missing.status_code == wrong.status_code == 401
    assert missing.get_json() == wrong.get_json()


@pytest.fixture
def limited_client():
    config.RATE_LIMIT_ENABLED = True
    try:
        app = create_app()
        limiter.reset()
        yield app.test_client()
    finally:
        limiter.reset()
        config.RATE_LIMIT_ENABLED = False


def test_login_rate_limit(limited_client):
    codes = [login(limited_client, "x", name="nikt").status_code for _ in range(12)]
    assert codes[:10] == [401] * 10
    assert 429 in codes[10:]


def test_register_rate_limit(limited_client):
    codes = [register_user(limited_client, f"user{i}").status_code for i in range(12)]
    assert codes[:10] == [201] * 10
    assert codes[10] == 429


def test_health_is_not_rate_limited(limited_client):
    assert all(limited_client.get("/api/health").status_code == 200 for _ in range(350))


def test_api_responses_have_security_headers(client):
    res = client.get("/api/posts")
    assert res.headers["Cache-Control"] == "no-store"
    assert res.headers["X-Content-Type-Options"] == "nosniff"
    assert res.headers["Cross-Origin-Resource-Policy"] == "same-origin"


def test_oversized_body_is_rejected(client):
    res = client.post("/api/auth/login", data="x" * (config.MAX_CONTENT_LENGTH + 1), content_type="application/json")
    assert res.status_code == 413


def test_production_requires_strong_secret(monkeypatch):
    monkeypatch.setattr(config, "APP_ENV", "production")
    monkeypatch.setattr(config, "SECRET_KEY", config.DEV_SECRET_KEY)
    with pytest.raises(RuntimeError):
        create_app()
    monkeypatch.setattr(config, "SECRET_KEY", "krotki")
    with pytest.raises(RuntimeError):
        create_app()
    monkeypatch.setattr(config, "SECRET_KEY", "x" * 32)
    create_app()

import json
import logging

import jwt
import pytest

from app import config
from app.db import query_one

PASSWORD = "sekretne-haslo-1"


def login_headers(client, name="anna", user_agent="przegladarka-1"):
    res = client.post(
        "/api/auth/login",
        json={"login": name, "password": PASSWORD},
        headers={"User-Agent": user_agent},
    )
    assert res.status_code == 200, res.get_json()
    return {"Authorization": f"Bearer {res.get_json()['token']}"}


def test_logout_revokes_token(client, register):
    headers, _ = register("anna")
    assert client.get("/api/auth/me", headers=headers).status_code == 200
    assert client.post("/api/auth/logout", headers=headers).status_code == 204
    assert client.get("/api/auth/me", headers=headers).status_code == 401


def test_token_without_session_is_rejected(client, register):
    _, user = register("anna")
    token = jwt.encode({"sub": str(user["id"]), "jti": "nieistniejaca"}, config.SECRET_KEY, algorithm="HS256")
    assert client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"}).status_code == 401
    legacy = jwt.encode({"sub": str(user["id"])}, config.SECRET_KEY, algorithm="HS256")
    assert client.get("/api/auth/me", headers={"Authorization": f"Bearer {legacy}"}).status_code == 401


def test_sessions_listing_marks_current(client, register):
    first, _ = register("anna")
    second = login_headers(client, user_agent="przegladarka-2")
    items = client.get("/api/auth/sessions", headers=second).get_json()["items"]
    assert len(items) == 2
    current = [i for i in items if i["current"]]
    assert len(current) == 1 and current[0]["user_agent"] == "przegladarka-2"
    assert client.get("/api/auth/sessions", headers=first).status_code == 200


def test_revoke_single_session(client, register):
    first, _ = register("anna")
    second = login_headers(client)
    items = client.get("/api/auth/sessions", headers=second).get_json()["items"]
    other = next(i for i in items if not i["current"])
    assert client.delete(f"/api/auth/sessions/{other['id']}", headers=second).status_code == 204
    assert client.get("/api/auth/me", headers=first).status_code == 401
    assert client.get("/api/auth/me", headers=second).status_code == 200
    assert client.delete(f"/api/auth/sessions/{other['id']}", headers=second).status_code == 404


def test_cannot_revoke_foreign_session(client, register):
    register("anna")
    other, _ = register("bob")
    anna = login_headers(client, "anna")
    anna_session = client.get("/api/auth/sessions", headers=anna).get_json()["items"][0]["id"]
    assert client.delete(f"/api/auth/sessions/{anna_session}", headers=other).status_code == 404
    assert client.get("/api/auth/me", headers=anna).status_code == 200


def test_revoke_all_other_sessions_keeps_current(client, register):
    first, _ = register("anna")
    second = login_headers(client)
    third = login_headers(client)
    assert client.delete("/api/auth/sessions", headers=third).status_code == 204
    assert client.get("/api/auth/me", headers=first).status_code == 401
    assert client.get("/api/auth/me", headers=second).status_code == 401
    assert client.get("/api/auth/me", headers=third).status_code == 200


def test_last_seen_is_refreshed_after_interval(client, register):
    headers, _ = register("anna")
    query_one("UPDATE sessions SET last_seen = now() - interval '1 hour' RETURNING id")
    client.get("/api/auth/me", headers=headers)
    row = query_one("SELECT now() - last_seen AS age FROM sessions")
    assert row["age"].total_seconds() < 60


def test_sessions_require_login(client):
    assert client.get("/api/auth/sessions").status_code == 401
    assert client.post("/api/auth/logout").status_code == 401
    assert client.delete("/api/auth/sessions").status_code == 401


class Collector(logging.Handler):
    def __init__(self):
        super().__init__()
        self.records = []

    def emit(self, record):
        self.records.append(json.loads(record.getMessage()))


@pytest.fixture
def events():
    collector = Collector()
    logger = logging.getLogger("questlog.security")
    logger.addHandler(collector)
    yield collector.records
    logger.removeHandler(collector)


def test_security_events_are_logged(client, register, events):
    headers, user = register("anna")
    client.post("/api/auth/login", json={"login": "anna", "password": "zle-haslo-123"})
    client.post("/api/auth/logout", headers=headers)
    client.get("/api/auth/me")
    logged = list(events)
    names = [e["event"] for e in logged]
    assert names.count("register") == 1
    assert "login_failed" in names
    assert "logout" in names
    denied = [e for e in logged if e["event"] == "denied"]
    assert any(e["status"] == 401 and e["path"] == "/api/auth/me" for e in denied)
    assert all("zle-haslo-123" not in json.dumps(e) for e in logged)
    assert all(e["user_id"] == user["id"] for e in logged if e["event"] in ("register", "logout"))


def test_lockout_is_logged(client, register, events):
    register("anna")
    for _ in range(config.LOGIN_MAX_ATTEMPTS + 1):
        client.post("/api/auth/login", json={"login": "anna", "password": "zle-haslo-123"})
    names = [e["event"] for e in events]
    assert "account_locked" in names
    assert "login_blocked" in names

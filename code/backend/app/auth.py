import datetime as dt
import uuid
from functools import wraps

import jwt
from flask import g, jsonify, request

from . import config
from .db import query, query_one

LAST_SEEN_INTERVAL = dt.timedelta(minutes=1)


def make_token(user_id):
    session_id = uuid.uuid4().hex
    query(
        "DELETE FROM sessions WHERE user_id = %s AND created_at < now() - make_interval(hours => %s)",
        (user_id, config.TOKEN_TTL_HOURS),
    )
    query(
        "INSERT INTO sessions (id, user_id, ip, user_agent) VALUES (%s, %s, %s, %s)",
        (session_id, user_id, request.remote_addr, request.headers.get("User-Agent", "")[:255]),
    )
    payload = {
        "sub": str(user_id),
        "jti": session_id,
        "exp": dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=config.TOKEN_TTL_HOURS),
    }
    return jwt.encode(payload, config.SECRET_KEY, algorithm="HS256")


def _load_user():
    """Ustawia g.user (dict lub None) na podstawie nagłówka Authorization."""
    g.user = None
    g.session_id = None
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return
    try:
        data = jwt.decode(header[7:], config.SECRET_KEY, algorithms=["HS256"])
        row = query_one(
            """SELECT u.id, u.username, u.email, u.created_at, s.last_seen
               FROM sessions s JOIN users u ON u.id = s.user_id
               WHERE s.id = %s AND s.user_id = %s AND s.revoked_at IS NULL""",
            (data["jti"], int(data["sub"])),
        )
    except (jwt.PyJWTError, ValueError, KeyError):
        return
    if row is None:
        return
    if dt.datetime.now(dt.timezone.utc) - row.pop("last_seen") > LAST_SEEN_INTERVAL:
        query("UPDATE sessions SET last_seen = now() WHERE id = %s", (data["jti"],))
    g.user = row
    g.session_id = data["jti"]


def optional_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        _load_user()
        return fn(*args, **kwargs)

    return wrapper


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        _load_user()
        if g.user is None:
            return jsonify(error="Wymagane logowanie."), 401
        return fn(*args, **kwargs)

    return wrapper


def current_user_id():
    return g.user["id"] if g.get("user") else None

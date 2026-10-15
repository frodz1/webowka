import datetime as dt
from functools import wraps

import jwt
from flask import g, jsonify, request

from . import config
from .db import query_one


def make_token(user_id):
    payload = {
        "sub": str(user_id),
        "exp": dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=config.TOKEN_TTL_HOURS),
    }
    return jwt.encode(payload, config.SECRET_KEY, algorithm="HS256")


def _load_user():
    """Ustawia g.user (dict lub None) na podstawie nagłówka Authorization."""
    g.user = None
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return
    try:
        data = jwt.decode(header[7:], config.SECRET_KEY, algorithms=["HS256"])
        user = query_one("SELECT id, username, email, created_at FROM users WHERE id = %s", (int(data["sub"]),))
    except (jwt.PyJWTError, ValueError, KeyError):
        return
    g.user = user


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

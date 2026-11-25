import datetime as dt

import psycopg
from flask import Blueprint, g, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from . import config
from .auth import login_required, make_token
from .db import query_one
from .extensions import limiter
from .validation import EMAIL_RE, USERNAME_RE, ValidationError, check_password, clean_str

DUMMY_HASH = generate_password_hash("nieistniejace-haslo")

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _user_payload(user):
    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "created_at": user["created_at"],
    }


@bp.post("/register")
@limiter.limit("10 per hour")
def register():
    data = request.get_json(silent=True) or {}
    try:
        username = clean_str(data, "username", required=True, label="nazwa użytkownika")
        email = clean_str(data, "email", required=True, max_len=255, label="e-mail")
        password = check_password(data.get("password"))
    except ValidationError as exc:
        return jsonify(error=exc.message), 400

    if not USERNAME_RE.match(username):
        return jsonify(error="Nazwa użytkownika: 3–32 znaki (litery, cyfry, „_”)."), 400
    if not EMAIL_RE.match(email):
        return jsonify(error="Podaj poprawny adres e-mail."), 400

    try:
        user = query_one(
            """INSERT INTO users (username, email, password_hash)
               VALUES (%s, %s, %s)
               RETURNING id, username, email, created_at""",
            (username, email.lower(), generate_password_hash(password)),
        )
    except psycopg.errors.UniqueViolation:
        return jsonify(error="Nazwa użytkownika lub e-mail jest już zajęty."), 409

    return jsonify(token=make_token(user["id"]), user=_user_payload(user)), 201


@bp.post("/login")
@limiter.limit("10 per minute")
def login():
    data = request.get_json(silent=True) or {}
    login_name = str(data.get("login") or data.get("username") or "").strip()
    password = data.get("password") or ""
    user = query_one(
        "SELECT * FROM users WHERE lower(username) = lower(%s) OR lower(email) = lower(%s)",
        (login_name, login_name),
    )
    if user and user["locked_until"] and user["locked_until"] > dt.datetime.now(dt.timezone.utc):
        return jsonify(error="Zbyt wiele nieudanych prób. Spróbuj ponownie później."), 429
    hash_to_check = user["password_hash"] if user else DUMMY_HASH
    valid = isinstance(password, str) and check_password_hash(hash_to_check, password)
    if not user or not valid:
        if user:
            query_one(
                """UPDATE users SET
                       failed_logins = CASE WHEN failed_logins + 1 >= %(max)s THEN 0 ELSE failed_logins + 1 END,
                       locked_until = CASE WHEN failed_logins + 1 >= %(max)s
                                           THEN now() + make_interval(mins => %(mins)s)
                                           ELSE locked_until END
                   WHERE id = %(id)s RETURNING id""",
                {"max": config.LOGIN_MAX_ATTEMPTS, "mins": config.LOGIN_LOCK_MINUTES, "id": user["id"]},
            )
        return jsonify(error="Nieprawidłowy login lub hasło."), 401
    query_one("UPDATE users SET failed_logins = 0, locked_until = NULL WHERE id = %s RETURNING id", (user["id"],))
    return jsonify(token=make_token(user["id"]), user=_user_payload(user))


@bp.get("/me")
@login_required
def me():
    return jsonify(user=_user_payload(g.user))

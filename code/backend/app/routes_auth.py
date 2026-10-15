import psycopg
from flask import Blueprint, g, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from .auth import login_required, make_token
from .db import query_one
from .validation import EMAIL_RE, USERNAME_RE, ValidationError, clean_str

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _user_payload(user):
    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "created_at": user["created_at"],
    }


@bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    try:
        username = clean_str(data, "username", required=True, label="nazwa użytkownika")
        email = clean_str(data, "email", required=True, max_len=255, label="e-mail")
        password = data.get("password")
    except ValidationError as exc:
        return jsonify(error=exc.message), 400

    if not USERNAME_RE.match(username):
        return jsonify(error="Nazwa użytkownika: 3–32 znaki (litery, cyfry, „_”)."), 400
    if not EMAIL_RE.match(email):
        return jsonify(error="Podaj poprawny adres e-mail."), 400
    if not isinstance(password, str) or len(password) < 6:
        return jsonify(error="Hasło musi mieć co najmniej 6 znaków."), 400

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
def login():
    data = request.get_json(silent=True) or {}
    login_name = str(data.get("login") or data.get("username") or "").strip()
    password = data.get("password") or ""
    user = query_one(
        "SELECT * FROM users WHERE lower(username) = lower(%s) OR lower(email) = lower(%s)",
        (login_name, login_name),
    )
    if not user or not isinstance(password, str) or not check_password_hash(user["password_hash"], password):
        return jsonify(error="Nieprawidłowy login lub hasło."), 401
    return jsonify(token=make_token(user["id"]), user=_user_payload(user))


@bp.get("/me")
@login_required
def me():
    return jsonify(user=_user_payload(g.user))

from flask import Blueprint, g, jsonify, request

from .auth import current_user_id, login_required, optional_auth
from .db import query, query_one
from .validation import ValidationError, clean_str
from .votes import apply_vote

bp = Blueprint("comments", __name__, url_prefix="/api")

DELETED_BODY = "[usunięto]"

COMMENT_SELECT = """
    SELECT c.id, c.post_id, c.parent_id, c.deleted, c.created_at, c.updated_at,
           CASE WHEN c.deleted THEN %(deleted_body)s ELSE c.body END AS body,
           CASE WHEN c.deleted THEN NULL ELSE c.author_id END AS author_id,
           CASE WHEN c.deleted THEN NULL ELSE u.username END AS author,
           COALESCE((SELECT SUM(value) FROM votes WHERE comment_id = c.id), 0)::int AS score,
           (SELECT value FROM votes WHERE comment_id = c.id AND user_id = %(uid)s) AS my_vote
    FROM comments c
    JOIN users u ON u.id = c.author_id
"""


def fetch_comment(comment_id):
    return query_one(
        COMMENT_SELECT + " WHERE c.id = %(id)s",
        {"id": comment_id, "uid": current_user_id(), "deleted_body": DELETED_BODY},
    )


def _body():
    return clean_str(request.get_json(silent=True) or {}, "body", required=True, max_len=5000, label="treść")


@bp.get("/posts/<int:post_id>/comments")
@optional_auth
def list_comments(post_id):
    """Płaska lista (parent_id wskazuje rodzica); drzewo albo płaski widok składa front-end."""
    if not query_one("SELECT 1 AS x FROM posts WHERE id = %s", (post_id,)):
        return jsonify(error="Nie znaleziono wpisu."), 404
    rows = query(
        COMMENT_SELECT + " WHERE c.post_id = %(post_id)s ORDER BY c.created_at, c.id",
        {"post_id": post_id, "uid": current_user_id(), "deleted_body": DELETED_BODY},
    )
    return jsonify(items=rows)


@bp.post("/posts/<int:post_id>/comments")
@login_required
def create_comment(post_id):
    if not query_one("SELECT 1 AS x FROM posts WHERE id = %s", (post_id,)):
        return jsonify(error="Nie znaleziono wpisu."), 404
    try:
        body = _body()
    except ValidationError as exc:
        return jsonify(error=exc.message), 400

    parent_id = (request.get_json(silent=True) or {}).get("parent_id")
    if parent_id is not None:
        parent = None
        if isinstance(parent_id, int) and not isinstance(parent_id, bool):
            parent = query_one("SELECT post_id, deleted FROM comments WHERE id = %s", (parent_id,))
        if not parent or parent["post_id"] != post_id:
            return jsonify(error="Komentarz nadrzędny nie istnieje w tym wpisie."), 400
        if parent["deleted"]:
            return jsonify(error="Nie można odpowiedzieć na usunięty komentarz."), 400

    row = query_one(
        "INSERT INTO comments (post_id, author_id, parent_id, body) VALUES (%s, %s, %s, %s) RETURNING id",
        (post_id, g.user["id"], parent_id, body),
    )
    return jsonify(comment=fetch_comment(row["id"])), 201


def _own_comment(comment_id, verb):
    comment = query_one("SELECT author_id, deleted FROM comments WHERE id = %s", (comment_id,))
    if not comment or comment["deleted"]:
        return jsonify(error="Nie znaleziono komentarza."), 404
    if comment["author_id"] != g.user["id"]:
        return jsonify(error=f"Możesz {verb} tylko własne komentarze."), 403
    return None


@bp.put("/comments/<int:comment_id>")
@login_required
def update_comment(comment_id):
    error = _own_comment(comment_id, "edytować")
    if error:
        return error
    try:
        body = _body()
    except ValidationError as exc:
        return jsonify(error=exc.message), 400
    query("UPDATE comments SET body = %s, updated_at = now() WHERE id = %s", (body, comment_id))
    return jsonify(comment=fetch_comment(comment_id))


@bp.delete("/comments/<int:comment_id>")
@login_required
def delete_comment(comment_id):
    """Komentarz z odpowiedziami zostaje jako „[usunięto]”, aby nie zerwać wątku."""
    error = _own_comment(comment_id, "usuwać")
    if error:
        return error
    has_replies = query_one("SELECT 1 AS x FROM comments WHERE parent_id = %s LIMIT 1", (comment_id,))
    if has_replies:
        query("UPDATE comments SET deleted = TRUE, body = '', updated_at = now() WHERE id = %s", (comment_id,))
        query("DELETE FROM votes WHERE comment_id = %s", (comment_id,))
    else:
        query("DELETE FROM comments WHERE id = %s", (comment_id,))
    return "", 204


@bp.post("/comments/<int:comment_id>/vote")
@login_required
def vote_comment(comment_id):
    comment = query_one("SELECT deleted FROM comments WHERE id = %s", (comment_id,))
    if not comment or comment["deleted"]:
        return jsonify(error="Nie znaleziono komentarza."), 404
    return apply_vote("comment_id", comment_id)


@bp.get("/me/comments")
@login_required
def my_comments():
    rows = query(
        """SELECT c.id, c.post_id, c.parent_id, c.body, c.created_at, c.updated_at,
                  p.title AS post_title,
                  COALESCE((SELECT SUM(value) FROM votes WHERE comment_id = c.id), 0)::int AS score
           FROM comments c
           JOIN posts p ON p.id = c.post_id
           WHERE c.author_id = %s AND NOT c.deleted
           ORDER BY c.created_at DESC""",
        (g.user["id"],),
    )
    return jsonify(items=rows)

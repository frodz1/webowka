from flask import Blueprint, g, jsonify, request

from . import config
from .auth import current_user_id, login_required, optional_auth
from .db import query, query_one
from .validation import ValidationError, post_fields
from .votes import apply_vote

bp = Blueprint("posts", __name__, url_prefix="/api")

# Gorące: wynik tłumiony wiekiem wpisu (zbliżone do rankingu Hacker News).
SORTS = {
    "hot": "score::float / power(extract(epoch FROM (now() - created_at)) / 3600.0 + 2, 1.5) DESC, created_at DESC",
    "new": "created_at DESC",
    "best": "score DESC, created_at DESC",
}

POST_SELECT = """
    SELECT p.id, p.title, p.url, p.body, p.tag, p.created_at, p.updated_at,
           p.author_id, u.username AS author,
           COALESCE((SELECT SUM(value) FROM votes WHERE post_id = p.id), 0)::int AS score,
           (SELECT COUNT(*) FROM comments c WHERE c.post_id = p.id AND NOT c.deleted)::int AS comment_count,
           (SELECT value FROM votes WHERE post_id = p.id AND user_id = %(uid)s) AS my_vote
    FROM posts p
    JOIN users u ON u.id = p.author_id
"""


def fetch_posts(where="TRUE", params=None, sort="new", page=1):
    params = dict(params or {})
    params["uid"] = current_user_id()
    order = SORTS.get(sort, SORTS["hot"])
    per_page = config.PER_PAGE
    total = query_one(f"SELECT COUNT(*)::int AS n FROM posts p WHERE {where}", params)["n"]
    params.update(limit=per_page, offset=(page - 1) * per_page)
    items = query(
        f"""SELECT * FROM ({POST_SELECT} WHERE {where}) AS t
            ORDER BY {order} LIMIT %(limit)s OFFSET %(offset)s""",
        params,
    )
    return {
        "items": items,
        "page": page,
        "pages": max(1, -(-total // per_page)),
        "total": total,
    }


def fetch_post(post_id):
    return query_one(POST_SELECT + " WHERE p.id = %(id)s", {"id": post_id, "uid": current_user_id()})


def _page_arg():
    try:
        return max(1, int(request.args.get("page", 1)))
    except ValueError:
        return 1


@bp.get("/posts")
@optional_auth
def list_posts():
    sort = request.args.get("sort", "hot")
    if sort not in SORTS:
        sort = "hot"
    tag = (request.args.get("tag") or "").strip().lstrip("#").lower()
    where, params = ("p.tag = %(tag)s", {"tag": tag}) if tag else ("TRUE", {})
    return jsonify(fetch_posts(where, params, sort, _page_arg()))


@bp.get("/tags")
def list_tags():
    rows = query(
        "SELECT tag, COUNT(*)::int AS count FROM posts WHERE tag IS NOT NULL GROUP BY tag ORDER BY count DESC, tag LIMIT 30"
    )
    return jsonify(items=rows)


@bp.post("/posts")
@login_required
def create_post():
    try:
        fields = post_fields(request.get_json(silent=True) or {})
    except ValidationError as exc:
        return jsonify(error=exc.message), 400
    row = query_one(
        """INSERT INTO posts (title, url, body, tag, author_id)
           VALUES (%(title)s, %(url)s, %(body)s, %(tag)s, %(author_id)s) RETURNING id""",
        {**fields, "author_id": g.user["id"]},
    )
    return jsonify(post=fetch_post(row["id"])), 201


@bp.get("/posts/<int:post_id>")
@optional_auth
def get_post(post_id):
    post = fetch_post(post_id)
    if not post:
        return jsonify(error="Nie znaleziono wpisu."), 404
    return jsonify(post=post)


@bp.put("/posts/<int:post_id>")
@login_required
def update_post(post_id):
    existing = query_one("SELECT author_id FROM posts WHERE id = %s", (post_id,))
    if not existing:
        return jsonify(error="Nie znaleziono wpisu."), 404
    if existing["author_id"] != g.user["id"]:
        return jsonify(error="Możesz edytować tylko własne wpisy."), 403
    try:
        fields = post_fields(request.get_json(silent=True) or {})
    except ValidationError as exc:
        return jsonify(error=exc.message), 400
    query(
        """UPDATE posts SET title = %(title)s, url = %(url)s, body = %(body)s, tag = %(tag)s,
                            updated_at = now()
           WHERE id = %(id)s""",
        {**fields, "id": post_id},
    )
    return jsonify(post=fetch_post(post_id))


@bp.delete("/posts/<int:post_id>")
@login_required
def delete_post(post_id):
    existing = query_one("SELECT author_id FROM posts WHERE id = %s", (post_id,))
    if not existing:
        return jsonify(error="Nie znaleziono wpisu."), 404
    if existing["author_id"] != g.user["id"]:
        return jsonify(error="Możesz usuwać tylko własne wpisy."), 403
    query("DELETE FROM posts WHERE id = %s", (post_id,))
    return "", 204


@bp.post("/posts/<int:post_id>/vote")
@login_required
def vote_post(post_id):
    if not query_one("SELECT 1 AS x FROM posts WHERE id = %s", (post_id,)):
        return jsonify(error="Nie znaleziono wpisu."), 404
    return apply_vote("post_id", post_id)


@bp.get("/me/posts")
@login_required
def my_posts():
    return jsonify(fetch_posts("p.author_id = %(author)s", {"author": g.user["id"]}, "new", _page_arg()))

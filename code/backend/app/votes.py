from flask import g, jsonify, request

from .db import query_one

VALUE_ERROR = "Wartość głosu musi wynosić 1, -1 lub 0 (cofnięcie głosu)."


def apply_vote(target_column, target_id):
    """Zapisuje głos bieżącego użytkownika (+1, -1 lub 0 = cofnięcie) i zwraca nowy wynik."""
    assert target_column in ("post_id", "comment_id")
    value = (request.get_json(silent=True) or {}).get("value")
    if isinstance(value, bool) or value not in (1, -1, 0):
        return jsonify(error=VALUE_ERROR), 400

    uid = g.user["id"]
    if value == 0:
        query_one(f"DELETE FROM votes WHERE user_id = %s AND {target_column} = %s RETURNING 1 AS x", (uid, target_id))
    else:
        query_one(
            f"""INSERT INTO votes (user_id, {target_column}, value) VALUES (%s, %s, %s)
                ON CONFLICT (user_id, {target_column}) WHERE {target_column} IS NOT NULL
                DO UPDATE SET value = EXCLUDED.value
                RETURNING 1 AS x""",
            (uid, target_id, value),
        )
    score = query_one(
        f"SELECT COALESCE(SUM(value), 0)::int AS score FROM votes WHERE {target_column} = %s", (target_id,)
    )["score"]
    return jsonify(score=score, my_vote=value or None)

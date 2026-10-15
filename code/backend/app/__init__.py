import datetime as dt

from flask import Flask, jsonify
from flask.json.provider import DefaultJSONProvider
from werkzeug.exceptions import HTTPException


class JSONProvider(DefaultJSONProvider):
    ensure_ascii = False

    @staticmethod
    def default(o):
        if isinstance(o, (dt.datetime, dt.date)):
            return o.isoformat()
        return DefaultJSONProvider.default(o)


def create_app():
    app = Flask(__name__)
    app.json = JSONProvider(app)

    from . import routes_auth, routes_comments, routes_posts

    app.register_blueprint(routes_auth.bp)
    app.register_blueprint(routes_posts.bp)
    app.register_blueprint(routes_comments.bp)

    @app.get("/api/health")
    def health():
        return jsonify(status="ok")

    @app.errorhandler(HTTPException)
    def http_error(exc):
        return jsonify(error=exc.description), exc.code

    return app

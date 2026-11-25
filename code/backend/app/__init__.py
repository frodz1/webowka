import datetime as dt

from flask import Flask, jsonify, request
from flask.json.provider import DefaultJSONProvider
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.proxy_fix import ProxyFix

from . import config
from .extensions import limiter


class JSONProvider(DefaultJSONProvider):
    ensure_ascii = False

    @staticmethod
    def default(o):
        if isinstance(o, (dt.datetime, dt.date)):
            return o.isoformat()
        return DefaultJSONProvider.default(o)


def create_app():
    config.check_production()
    app = Flask(__name__)
    app.json = JSONProvider(app)
    app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_LENGTH
    app.config["RATELIMIT_ENABLED"] = config.RATE_LIMIT_ENABLED
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=config.PROXY_HOPS)
    limiter.init_app(app)

    from . import routes_auth, routes_comments, routes_posts

    app.register_blueprint(routes_auth.bp)
    app.register_blueprint(routes_posts.bp)
    app.register_blueprint(routes_comments.bp)

    @app.get("/api/health")
    @limiter.exempt
    def health():
        return jsonify(status="ok")

    @app.errorhandler(HTTPException)
    def http_error(exc):
        if exc.code == 429:
            return jsonify(error="Zbyt wiele żądań. Spróbuj ponownie za chwilę."), 429
        return jsonify(error=exc.description), exc.code

    @app.after_request
    def security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        if request.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    return app

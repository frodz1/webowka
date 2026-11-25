import os

DEV_SECRET_KEY = "dev-secret-change-me"

APP_ENV = os.environ.get("APP_ENV", "development")
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://questlog:questlog@localhost:5432/questlog")
SECRET_KEY = os.environ.get("SECRET_KEY", DEV_SECRET_KEY)
TOKEN_TTL_HOURS = int(os.environ.get("TOKEN_TTL_HOURS", "24"))
PER_PAGE = 20

MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", str(64 * 1024)))
PASSWORD_MIN_LEN = 10
PASSWORD_MAX_LEN = 128
LOGIN_MAX_ATTEMPTS = int(os.environ.get("LOGIN_MAX_ATTEMPTS", "5"))
LOGIN_LOCK_MINUTES = int(os.environ.get("LOGIN_LOCK_MINUTES", "15"))
RATE_LIMIT_ENABLED = os.environ.get("RATE_LIMIT_ENABLED", "1") == "1"
PROXY_HOPS = int(os.environ.get("PROXY_HOPS", "1"))


def check_production():
    if APP_ENV != "production":
        return
    if SECRET_KEY == DEV_SECRET_KEY or len(SECRET_KEY) < 32:
        raise RuntimeError("SECRET_KEY w produkcji musi być własny i mieć co najmniej 32 znaki.")

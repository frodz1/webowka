import os

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://questlog:questlog@localhost:5432/questlog")
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
TOKEN_TTL_HOURS = int(os.environ.get("TOKEN_TTL_HOURS", "168"))
PER_PAGE = 20

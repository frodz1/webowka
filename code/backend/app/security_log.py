import datetime as dt
import json
import logging
import sys

from flask import has_request_context, request

logger = logging.getLogger("questlog.security")
logger.setLevel(logging.INFO)
logger.propagate = False
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)


def log_event(event, **fields):
    record = {"ts": dt.datetime.now(dt.timezone.utc).isoformat(), "event": event}
    if has_request_context():
        record["ip"] = request.remote_addr
    record.update({k: v for k, v in fields.items() if v is not None})
    logger.info(json.dumps(record, ensure_ascii=False))

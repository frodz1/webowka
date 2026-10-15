import re

USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,32}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
TAG_RE = re.compile(r"^[\w-]{1,32}$")
URL_RE = re.compile(r"^https?://\S+$", re.IGNORECASE)


class ValidationError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


def clean_str(data, key, required=False, max_len=None, min_len=0, label=None):
    label = label or key
    value = data.get(key)
    if value is None or (isinstance(value, str) and not value.strip()):
        if required:
            raise ValidationError(f"Pole „{label}” jest wymagane.")
        return None
    if not isinstance(value, str):
        raise ValidationError(f"Pole „{label}” musi być tekstem.")
    value = value.strip()
    if len(value) < min_len:
        raise ValidationError(f"Pole „{label}” musi mieć co najmniej {min_len} znaki.")
    if max_len and len(value) > max_len:
        raise ValidationError(f"Pole „{label}” może mieć maksymalnie {max_len} znaków.")
    return value


def post_fields(data):
    """Waliduje pola wpisu: tytuł, link lub krótki tekst, opcjonalny tag."""
    title = clean_str(data, "title", required=True, min_len=3, max_len=200, label="tytuł")
    url = clean_str(data, "url", max_len=2000, label="link")
    body = clean_str(data, "body", max_len=5000, label="tekst")
    tag = clean_str(data, "tag", max_len=32, label="tag")
    if url and not URL_RE.match(url):
        raise ValidationError("Link musi zaczynać się od http:// lub https://.")
    if not url and not body:
        raise ValidationError("Podaj link albo krótki tekst.")
    if tag:
        tag = tag.lstrip("#").lower()
        if not TAG_RE.match(tag):
            raise ValidationError("Tag może zawierać litery, cyfry, „_” i „-”.")
    return {"title": title, "url": url, "body": body, "tag": tag or None}

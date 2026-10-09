CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    username      VARCHAR(32)  NOT NULL,
    email         VARCHAR(255) NOT NULL,
    password_hash TEXT         NOT NULL,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS users_username_lower_key ON users (lower(username));
CREATE UNIQUE INDEX IF NOT EXISTS users_email_lower_key    ON users (lower(email));

CREATE TABLE IF NOT EXISTS posts (
    id         SERIAL PRIMARY KEY,
    title      VARCHAR(200) NOT NULL,
    url        TEXT,
    body       TEXT,
    tag        VARCHAR(32),
    author_id  INTEGER      NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ,
    CONSTRAINT posts_url_or_body CHECK (url IS NOT NULL OR body IS NOT NULL)
);
CREATE INDEX IF NOT EXISTS posts_created_at_idx ON posts (created_at DESC);
CREATE INDEX IF NOT EXISTS posts_tag_idx        ON posts (tag);
CREATE INDEX IF NOT EXISTS posts_author_idx     ON posts (author_id);

-- parent_id jest puste dla komentarza głównego; dzięki temu powstaje drzewo.
CREATE TABLE IF NOT EXISTS comments (
    id         SERIAL PRIMARY KEY,
    post_id    INTEGER     NOT NULL REFERENCES posts (id)    ON DELETE CASCADE,
    author_id  INTEGER     NOT NULL REFERENCES users (id)    ON DELETE CASCADE,
    parent_id  INTEGER              REFERENCES comments (id) ON DELETE CASCADE,
    body       TEXT        NOT NULL,
    deleted    BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS comments_post_idx   ON comments (post_id);
CREATE INDEX IF NOT EXISTS comments_parent_idx ON comments (parent_id);
CREATE INDEX IF NOT EXISTS comments_author_idx ON comments (author_id);

-- Głos dotyczy dokładnie jednego z: wpisu albo komentarza.
CREATE TABLE IF NOT EXISTS votes (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER     NOT NULL REFERENCES users (id)    ON DELETE CASCADE,
    post_id    INTEGER              REFERENCES posts (id)    ON DELETE CASCADE,
    comment_id INTEGER              REFERENCES comments (id) ON DELETE CASCADE,
    value      SMALLINT    NOT NULL CHECK (value IN (-1, 1)),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT votes_one_target CHECK ((post_id IS NULL) <> (comment_id IS NULL))
);
-- Unikalna para użytkownik + element.
CREATE UNIQUE INDEX IF NOT EXISTS votes_user_post_key    ON votes (user_id, post_id)    WHERE post_id IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS votes_user_comment_key ON votes (user_id, comment_id) WHERE comment_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS votes_post_idx    ON votes (post_id)    WHERE post_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS votes_comment_idx ON votes (comment_id) WHERE comment_id IS NOT NULL;

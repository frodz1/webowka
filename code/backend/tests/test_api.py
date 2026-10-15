def make_post(client, headers, **overrides):
    payload = {"title": "Ciekawy link", "url": "https://example.com", "tag": "Tech"}
    payload.update(overrides)
    res = client.post("/api/posts", json=payload, headers=headers)
    assert res.status_code == 201, res.get_json()
    return res.get_json()["post"]


def test_register_login_and_me(client, register):
    headers, user = register("anna", "sekret123")
    assert client.get("/api/auth/me", headers=headers).get_json()["user"]["username"] == "anna"

    ok = client.post("/api/auth/login", json={"login": "ANNA", "password": "sekret123"})
    assert ok.status_code == 200 and ok.get_json()["token"]
    by_email = client.post("/api/auth/login", json={"login": "anna@example.com", "password": "sekret123"})
    assert by_email.status_code == 200
    bad = client.post("/api/auth/login", json={"login": "anna", "password": "zle"})
    assert bad.status_code == 401


def test_register_validation_and_duplicates(client, register):
    register("anna")
    dup = client.post("/api/auth/register", json={"username": "Anna", "email": "x@y.pl", "password": "sekret123"})
    assert dup.status_code == 409
    short = client.post("/api/auth/register", json={"username": "bob", "email": "b@y.pl", "password": "123"})
    assert short.status_code == 400
    bad_name = client.post("/api/auth/register", json={"username": "a b", "email": "c@y.pl", "password": "sekret123"})
    assert bad_name.status_code == 400


def test_write_endpoints_require_login(client):
    assert client.post("/api/posts", json={"title": "abc", "body": "x"}).status_code == 401
    assert client.post("/api/posts/1/vote", json={"value": 1}).status_code == 401
    assert client.post("/api/posts/1/comments", json={"body": "x"}).status_code == 401
    assert client.get("/api/posts").status_code == 200


def test_post_crud_and_ownership(client, register):
    a, _ = register()
    b, _ = register()
    post = make_post(client, a)
    assert post["tag"] == "tech" and post["score"] == 0

    assert client.put(f"/api/posts/{post['id']}", json={"title": "Nowy tytuł", "body": "tekst"}, headers=b).status_code == 403
    upd = client.put(f"/api/posts/{post['id']}", json={"title": "Nowy tytuł", "body": "tekst"}, headers=a)
    assert upd.status_code == 200 and upd.get_json()["post"]["title"] == "Nowy tytuł"

    assert client.delete(f"/api/posts/{post['id']}", headers=b).status_code == 403
    assert client.delete(f"/api/posts/{post['id']}", headers=a).status_code == 204
    assert client.get(f"/api/posts/{post['id']}").status_code == 404


def test_post_requires_link_or_text(client, register):
    a, _ = register()
    res = client.post("/api/posts", json={"title": "Sam tytuł"}, headers=a)
    assert res.status_code == 400
    res = client.post("/api/posts", json={"title": "Zły link", "url": "ftp://x"}, headers=a)
    assert res.status_code == 400


def test_voting_sum_change_and_undo(client, register):
    a, _ = register()
    b, _ = register()
    post = make_post(client, a)
    url = f"/api/posts/{post['id']}/vote"

    assert client.post(url, json={"value": 1}, headers=a).get_json() == {"score": 1, "my_vote": 1}
    assert client.post(url, json={"value": 1}, headers=b).get_json()["score"] == 2
    assert client.post(url, json={"value": -1}, headers=b).get_json() == {"score": 0, "my_vote": -1}
    # powtórzony głos tego samego użytkownika nie dubluje się
    assert client.post(url, json={"value": -1}, headers=b).get_json()["score"] == 0
    assert client.post(url, json={"value": 0}, headers=b).get_json() == {"score": 1, "my_vote": None}
    assert client.post(url, json={"value": 5}, headers=a).status_code == 400

    mine = client.get(f"/api/posts/{post['id']}", headers=a).get_json()["post"]
    assert mine["my_vote"] == 1 and mine["score"] == 1


def test_sorting_and_tag_filter(client, register):
    a, _ = register()
    b, _ = register()
    first = make_post(client, a, title="Pierwszy", tag="gry")
    second = make_post(client, a, title="Drugi", tag="nauka")
    client.post(f"/api/posts/{first['id']}/vote", json={"value": 1}, headers=a)
    client.post(f"/api/posts/{first['id']}/vote", json={"value": 1}, headers=b)

    def titles(qs):
        return [p["title"] for p in client.get("/api/posts?" + qs).get_json()["items"]]

    assert titles("sort=new") == ["Drugi", "Pierwszy"]
    assert titles("sort=best") == ["Pierwszy", "Drugi"]
    assert titles("sort=hot") == ["Pierwszy", "Drugi"]
    assert titles("tag=nauka") == ["Drugi"]
    assert {t["tag"] for t in client.get("/api/tags").get_json()["items"]} == {"gry", "nauka"}
    assert second["id"]


def test_comment_tree_votes_and_edit(client, register):
    a, _ = register()
    b, _ = register()
    post = make_post(client, a)
    base = f"/api/posts/{post['id']}/comments"

    root = client.post(base, json={"body": "Korzeń"}, headers=a).get_json()["comment"]
    reply = client.post(base, json={"body": "Odpowiedź", "parent_id": root["id"]}, headers=b).get_json()["comment"]
    assert reply["parent_id"] == root["id"]

    items = client.get(base).get_json()["items"]
    assert [c["id"] for c in items] == [root["id"], reply["id"]]
    assert client.get(f"/api/posts/{post['id']}").get_json()["post"]["comment_count"] == 2

    vote = client.post(f"/api/comments/{reply['id']}/vote", json={"value": 1}, headers=a)
    assert vote.get_json()["score"] == 1

    assert client.put(f"/api/comments/{root['id']}", json={"body": "x"}, headers=b).status_code == 403
    edited = client.put(f"/api/comments/{root['id']}", json={"body": "Zmieniony"}, headers=a)
    assert edited.get_json()["comment"]["body"] == "Zmieniony"


def test_comment_parent_must_belong_to_post(client, register):
    a, _ = register()
    p1 = make_post(client, a)
    p2 = make_post(client, a)
    c = client.post(f"/api/posts/{p1['id']}/comments", json={"body": "a"}, headers=a).get_json()["comment"]
    res = client.post(f"/api/posts/{p2['id']}/comments", json={"body": "b", "parent_id": c["id"]}, headers=a)
    assert res.status_code == 400


def test_delete_comment_keeps_thread(client, register):
    a, _ = register()
    b, _ = register()
    post = make_post(client, a)
    base = f"/api/posts/{post['id']}/comments"
    root = client.post(base, json={"body": "Korzeń"}, headers=a).get_json()["comment"]
    reply = client.post(base, json={"body": "Odp", "parent_id": root["id"]}, headers=b).get_json()["comment"]

    assert client.delete(f"/api/comments/{root['id']}", headers=a).status_code == 204
    items = {c["id"]: c for c in client.get(base).get_json()["items"]}
    assert items[root["id"]]["deleted"] and items[root["id"]]["body"] == "[usunięto]"
    assert items[root["id"]]["author"] is None

    # liść znika całkowicie
    assert client.delete(f"/api/comments/{reply['id']}", headers=b).status_code == 204
    assert reply["id"] not in {c["id"] for c in client.get(base).get_json()["items"]}


def test_my_content(client, register):
    a, _ = register()
    b, _ = register()
    mine = make_post(client, a, title="Mój wpis")
    make_post(client, b, title="Cudzy wpis")
    client.post(f"/api/posts/{mine['id']}/comments", json={"body": "Mój komentarz"}, headers=a)

    posts = client.get("/api/me/posts", headers=a).get_json()["items"]
    assert [p["title"] for p in posts] == ["Mój wpis"]
    comments = client.get("/api/me/comments", headers=a).get_json()["items"]
    assert [c["body"] for c in comments] == ["Mój komentarz"]
    assert comments[0]["post_title"] == "Mój wpis"

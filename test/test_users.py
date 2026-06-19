from sqlmodel import select
from app.models.file import File
from app.models.tag import Tag
from test.conftest import login, auth_header, upload_file

def test_read_rot(client):
    response = client.get("/")
    assert response.status_code == 200

    assert response.json() == {"message": "Welcome to the state of the art File upload system \"DODOload\""}

def test_create_user(client):
    response = client.post("/users", json={"email": "dodododododod@dododod.local", "password":"gagagagaga"})
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "password" not in data

    user_id = data["id"]

    login = client.post("/auth/login", json={"email": "dodododododod@dododod.local", "password": "gagagagaga"})
    token = login.json()["access_token"]

    response = client.get("/users", headers={"Authorization": f"Bearer {token}"})
    users = response.json()
    assert len(users) == 1
    assert users[0]["id"] == user_id

def test_duplicate_user(client, user_homer):
    response = client.post("/users", json={"email": user_homer.email, "password": user_homer.password})
    assert response.status_code == 409

def test_create_user_no_password(client):
    response = client.post("/users", json={"email": "dodododododod@dododod.local"})
    assert response.status_code == 422

def test_find_user_by_id(client):
    client.post("/users", json={"email": "dodododododod@dododod.local", "password":"gagagagaga"})
    response = client.get("/users/1")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "dodododododod@dododod.local"

def test_find_user_by_id_fail(client):
    response = client.get("/users/1")
    assert response.status_code == 404

def test_delete_current_user(client, user_homer):
    token = login(client, user_homer)

    response = client.delete("/users/me", headers=auth_header(token))
    assert response.status_code == 200
    assert response.json() == {"ok": True}

    # the user no longer exists
    assert client.get(f"/users/{user_homer.id}").status_code == 404

def test_delete_user_requires_auth(client):
    response = client.delete("/users/me")
    assert response.status_code == 401

def test_delete_user_removes_their_files_and_tags(client, user_homer, upload_dir, db):
    token = login(client, user_homer)
    tag_id = client.post("/tags/", json={"name": "urgent"}, headers=auth_header(token)).json()["id"]
    upload_file(client, token, tag_ids=[tag_id], filename="a.txt")
    upload_file(client, token, filename="b.txt")

    # both files are on disk before deletion
    assert len(list(upload_dir.iterdir())) == 2

    response = client.delete("/users/me", headers=auth_header(token))
    assert response.status_code == 200

    # files gone from disk
    assert list(upload_dir.iterdir()) == []
    assert db.exec(select(File)).all() == []
    assert db.exec(select(Tag)).all() == []
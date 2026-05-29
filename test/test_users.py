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
    response = client.post("/users", json={"email": "dodododododod@dododod.local", "password":"gagagagaga"})
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
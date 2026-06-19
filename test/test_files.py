from test.conftest import login, auth_header, upload_file

def test_upload_file(client, user_homer, upload_dir):
    token = login(client, user_homer)

    content = b"hello world"
    response = upload_file(client, token, content=content)
    assert response.status_code == 200

    data = response.json()
    assert data["filename"] == "hello.txt"
    assert data["content_type"] == "text/plain"
    assert data["size"] == len(content)
    assert data["user"]["id"] == user_homer.id

    # Was file actually written to disk
    stored = list(upload_dir.iterdir())
    assert len(stored) == 1
    assert stored[0].read_bytes() == content

def test_download_file(client, user_homer):
    token = login(client, user_homer)

    content = b"hello world"
    file_id = upload_file(client, token, content=content).json()["id"]

    response = client.get(f"/files/{file_id}", headers=auth_header(token))
    assert response.status_code == 200
    assert response.content == content

def test_download_other_users_file(client, user_homer, user_hesiod):
    homer_token = login(client, user_homer)
    file_id = upload_file(client, homer_token).json()["id"]

    hesiod_token = login(client, user_hesiod)
    response = client.get(f"/files/{file_id}", headers=auth_header(hesiod_token))
    assert response.status_code == 404

def test_delete_file(client, user_homer):
    token = login(client, user_homer)
    file_id = upload_file(client, token).json()["id"]

    response = client.delete(f"/files/{file_id}", headers=auth_header(token))
    assert response.status_code == 200
    assert response.json() == {"ok": True}

    # Authorized, File should be gone
    response = client.get(f"/files/{file_id}", headers=auth_header(token))
    assert response.status_code == 404

def test_delete_other_users_file(client, user_homer, user_hesiod):
    homer_token = login(client, user_homer)
    file_id = upload_file(client, homer_token).json()["id"]

    hesiod_token = login(client, user_hesiod)
    response = client.delete(f"/files/{file_id}", headers=auth_header(hesiod_token))
    assert response.status_code == 404

    # Unauthorized, File should be gone
    response = client.get(f"/files/{file_id}", headers=auth_header(homer_token))
    assert response.status_code == 200

from test.conftest import login, auth_header, upload_file

def create_tag(client, token, name="urgent"):
    return client.post("/tags/", json={"name": name}, headers=auth_header(token))

def test_create_tag(client, user_homer):
    token = login(client, user_homer)

    response = create_tag(client, token, name="urgent")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "urgent"
    assert data["user"]["id"] == user_homer.id

def test_create_tag_requires_auth(client):
    response = client.post("/tags/", json={"name": "urgent"})
    assert response.status_code == 401

def test_list_tags_only_returns_own(client, user_homer, user_hesiod):
    homer_token = login(client, user_homer)
    hesiod_token = login(client, user_hesiod)
    create_tag(client, homer_token, name="homer-tag")
    create_tag(client, hesiod_token, name="hesiod-tag")

    response = client.get("/tags/", headers=auth_header(homer_token))
    assert response.status_code == 200
    tags = response.json()
    assert len(tags) == 1
    assert tags[0]["name"] == "homer-tag"

def test_get_other_users_tag(client, user_homer, user_hesiod):
    homer_token = login(client, user_homer)
    tag_id = create_tag(client, homer_token).json()["id"]

    hesiod_token = login(client, user_hesiod)
    response = client.get(f"/tags/{tag_id}", headers=auth_header(hesiod_token))
    assert response.status_code == 404

def test_delete_tag(client, user_homer):
    token = login(client, user_homer)
    tag_id = create_tag(client, token).json()["id"]

    response = client.delete(f"/tags/{tag_id}", headers=auth_header(token))
    assert response.status_code == 200
    assert response.json() == {"ok": True}

    # the tag is gone afterwards
    response = client.get(f"/tags/{tag_id}", headers=auth_header(token))
    assert response.status_code == 404

def test_delete_other_users_tag(client, user_homer, user_hesiod):
    homer_token = login(client, user_homer)
    tag_id = create_tag(client, homer_token).json()["id"]

    hesiod_token = login(client, user_hesiod)
    response = client.delete(f"/tags/{tag_id}", headers=auth_header(hesiod_token))
    assert response.status_code == 404

    # the owner's tag is still there
    response = client.get(f"/tags/{tag_id}", headers=auth_header(homer_token))
    assert response.status_code == 200

def test_upload_file_without_tags(client, user_homer):
    token = login(client, user_homer)

    response = upload_file(client, token)
    assert response.status_code == 200
    assert response.json()["tags"] == []

def test_upload_file_with_tags(client, user_homer):
    token = login(client, user_homer)
    tag_id = create_tag(client, token).json()["id"]

    response = upload_file(client, token, tag_ids=[tag_id])
    assert response.status_code == 200
    assert [tag["id"] for tag in response.json()["tags"]] == [tag_id]

def test_upload_file_with_other_users_tag(client, user_homer, user_hesiod):
    homer_token = login(client, user_homer)
    hesiod_token = login(client, user_hesiod)
    hesiod_tag_id = create_tag(client, hesiod_token).json()["id"]

    response = upload_file(client, homer_token, tag_ids=[hesiod_tag_id])
    assert response.status_code == 404

def test_get_files_by_tag(client, user_homer):
    token = login(client, user_homer)
    tag_id = create_tag(client, token).json()["id"]
    file_id = upload_file(client, token, tag_ids=[tag_id]).json()["id"]

    response = client.get(f"/tags/{tag_id}/files", headers=auth_header(token))
    assert response.status_code == 200
    files = response.json()
    assert len(files) == 1
    assert files[0]["id"] == file_id

def test_get_files_by_other_users_tag(client, user_homer, user_hesiod):
    homer_token = login(client, user_homer)
    tag_id = create_tag(client, homer_token).json()["id"]

    hesiod_token = login(client, user_hesiod)
    response = client.get(f"/tags/{tag_id}/files", headers=auth_header(hesiod_token))
    assert response.status_code == 404

def test_delete_tag_removes_it_from_files(client, user_homer):
    token = login(client, user_homer)
    tag_id = create_tag(client, token).json()["id"]
    upload_file(client, token, tag_ids=[tag_id])

    # the file initially carries the tag
    files = client.get("/files/", headers=auth_header(token)).json()
    assert [tag["id"] for tag in files[0]["tags"]] == [tag_id]

    # deleting the tag detaches it from the file but keeps the file
    client.delete(f"/tags/{tag_id}", headers=auth_header(token))

    files = client.get("/files/", headers=auth_header(token)).json()
    assert len(files) == 1
    assert files[0]["tags"] == []

from pytest import fixture
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from app.main import app
from app.database import get_session
from app.models.user import User
from app.services import file as file_service


def login(client, user):
    response = client.post("/auth/login", json={"email": user.email, "password": user.password})
    return response.json()["access_token"]

def auth_header(token):
    return {"Authorization": f"Bearer {token}"}

def upload_file(client, token, tag_ids=None, filename="hello.txt", content=b"hello world", content_type="text/plain"):
    data = {"tag_ids": tag_ids} if tag_ids is not None else {}
    return client.post(
        "/files/",
        files={"upload": (filename, content, content_type)},
        data=data,
        headers=auth_header(token),
    )


@fixture(autouse=True)
def upload_dir(tmp_path, monkeypatch):
    # Change Upload folder to different location for tests.
    test_dir = tmp_path / "uploads"
    # Restore original upload location after tests.
    monkeypatch.setattr(file_service, "UPLOAD_DIR", test_dir)
    return test_dir


@fixture
def db():
    sqlite_file_name = "database_test.db"
    sqlite_url = f"sqlite:///{sqlite_file_name}"

    connect_args = {"check_same_thread": False}
    engine = create_engine(sqlite_url, connect_args=connect_args)

    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    with Session(engine) as session:
        yield session

    # Teardown: drop the override and close the engine's connections so each
    # test cleans up after itself (no leaked sqlite connections).
    app.dependency_overrides.clear()
    engine.dispose()

@fixture
def client(db):
    return TestClient(app)

@fixture
def user_homer(db):
    homer = User()
    homer.email="homer@ithaca.gr"
    homer.password="Odyssey"

    db.add(homer)
    db.commit()
    db.refresh(homer)

    return homer

@fixture
def user_hesiod(db):
    hesiod = User()
    hesiod.email="hesiod@boeotia.gr"
    hesiod.password="works-and-days"

    db.add(hesiod)
    db.commit()
    db.refresh(hesiod)

    return hesiod
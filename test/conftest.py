from pytest import fixture
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from app.main import app
from app.database import get_session
from app.models.user import User


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

    return Session(engine)

@fixture
def client(db):
    return TestClient(app)

@fixture
def user_homer(db):
    homer = User()
    homer.email="dodododododod@dododod.local"
    homer.password="gagagagaga"

    db.add(homer)
    db.commit()
    db.refresh(homer)

    return homer
import os
from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

# DATABASE_URL wins whenever it is set, e.g. Postgres via docker compose:
#   DATABASE_URL=postgresql+psycopg://dodoload:dodoload@localhost:5432/dodoload
# Without it the app falls back to SQLite. That path stays overridable so
# deployments can point it at a persistent volume.
database_url = os.environ.get("DATABASE_URL")

if not database_url:
    sqlite_file_name = os.environ.get("DATABASE_FILE", "database.db")
    database_url = f"sqlite:///{sqlite_file_name}"

# check_same_thread is a SQLite-only connect argument.
connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}

engine = create_engine(database_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

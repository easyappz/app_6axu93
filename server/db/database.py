from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

DB_DIR = Path(__file__).resolve().parent.parent
DB_PATH = DB_DIR / "app.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    future=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    # Import models to register metadata
    from server.models.user import User  # noqa: F401
    from server.models.listing import Listing  # noqa: F401
    from server.models.comment import Comment  # noqa: F401

    Base.metadata.create_all(bind=engine)

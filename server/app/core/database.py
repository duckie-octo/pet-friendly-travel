from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.core.config import get_settings

settings = get_settings()

_connect_args = (
    {"check_same_thread": False}
    if settings.trips_database_url.startswith("sqlite")
    else {}
)


def _engine(url: str):
    args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=args)


userprofile_engine = _engine(settings.userprofile_database_url)
trips_engine = _engine(settings.trips_database_url)

# Backward-compatible default session (trip / booking data)
engine = trips_engine

UserProfileSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=userprofile_engine)
TripsSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=trips_engine)
SessionLocal = TripsSessionLocal

UserProfileBase = declarative_base()
TripsBase = declarative_base()
# Legacy alias
Base = TripsBase


def get_userprofile_db():
    db = UserProfileSessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_trips_db():
    db = TripsSessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db():
    """Trip/booking database session (alias for get_trips_db)."""
    yield from get_trips_db()

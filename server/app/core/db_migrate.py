from sqlalchemy import inspect, text

from app.core.config import get_settings
from app.core.database import trips_engine, userprofile_engine
from app.models import trips_schema as trips_models  # noqa: F401
from app.models import userprofile as userprofile_models  # noqa: F401
from app.models.trips_schema import TripsBase
from app.models.userprofile import User, UserProfileBase


def ensure_trips_schema() -> None:
    inspector = inspect(trips_engine)
    if inspector.has_table("trips"):
        return
    TripsBase.metadata.create_all(bind=trips_engine)


def _users_table_valid(inspector) -> bool:
    if not inspector.has_table("users"):
        return False
    columns = {col["name"] for col in inspector.get_columns("users")}
    return {"id", "email", "password_hash", "full_name"}.issubset(columns)


def ensure_userprofile_schema() -> None:
    inspector = inspect(userprofile_engine)
    if _users_table_valid(inspector):
        return

    if inspector.has_table("users") and str(userprofile_engine.url).startswith("sqlite"):
        with userprofile_engine.begin() as conn:
            conn.execute(text("DROP TABLE IF EXISTS users"))

    User.__table__.create(bind=userprofile_engine, checkfirst=True)


def ensure_database_initialized() -> None:
    ensure_trips_schema()


def ensure_auth_schema() -> None:
    ensure_trips_schema()
    ensure_userprofile_schema()

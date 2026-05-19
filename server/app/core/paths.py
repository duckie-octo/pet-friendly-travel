from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
INIT_DB_SQL = APP_DIR / "schemas" / "init_db.sql"
SCHEMA_SQL = APP_DIR / "schemas" / "schema.sql"

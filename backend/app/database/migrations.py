from sqlalchemy import text
from sqlalchemy.engine import Engine


def _column_exists(engine: Engine, table: str, column: str) -> bool:
    with engine.connect() as conn:
        rows = conn.execute(text(f"PRAGMA table_info({table})")).fetchall()
    return any(row[1] == column for row in rows)


def run_migrations(engine: Engine) -> None:
    additions = [
        ("reviews", "review_title",      "TEXT"),
        ("reviews", "ensemble_score",    "REAL"),
        ("reviews", "model_scores_json", "TEXT"),
    ]
    with engine.begin() as conn:
        for table, column, col_type in additions:
            if not _column_exists(engine, table, column):
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"))
                print(f"[migration] Added column {table}.{column}")

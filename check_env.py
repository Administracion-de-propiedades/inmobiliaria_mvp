from __future__ import annotations

import sys
from pathlib import Path


# Ensure `src` is on the import path when running from project root
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

from config.settings import settings  # type: ignore  # noqa: E402


def main() -> None:
    print(f"Engine: {settings.DB_ENGINE}")

    # Lazy import to avoid optional dependency issues in environments
    from core.database import Database  # type: ignore  # noqa: E402

    try:
        db = Database()
        conn = db.connect()
        # Simple no-op query per engine (SQLite is default)
        try:
            if settings.DB_ENGINE == "sqlite":
                conn.execute("SELECT 1")
            else:
                # For PostgreSQL, a basic check if connection is open
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
        finally:
            db.close()
        print(f"Connected successfully to {settings.DB_NAME}")
    except Exception as exc:  # pragma: no cover - diagnostic script
        print(f"Connection failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()


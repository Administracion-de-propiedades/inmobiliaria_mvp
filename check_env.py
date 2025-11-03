from __future__ import annotations

import sys
from pathlib import Path


# Ensure `src` is on the import path when running from project root
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

from config.settings import get_settings  # type: ignore  # noqa: E402


def main() -> None:
    settings = get_settings()
    print(f"Engine: {settings.db_engine}")

    # Lazy import to avoid optional dependency issues in environments
    from core.database import Database  # type: ignore  # noqa: E402

    try:
        db = Database()
        conn = db.connect()
        try:
            conn.execute("SELECT 1")
        finally:
            db.close()
        target = settings.sqlite_path if settings.db_engine == "sqlite" else settings.db_name
        print(f"Connected successfully to {target}")
    except NotImplementedError as exc:
        print(f"Connection path not implemented: {exc}")
        sys.exit(2)
    except Exception as exc:  # pragma: no cover - diagnostic script
        print(f"Connection failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()

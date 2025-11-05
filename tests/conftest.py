import os
import sys
import subprocess
from pathlib import Path
import pytest

# Ensure project 'src' is importable
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

TEST_DB_DIR = Path("tests/.tmp")
TEST_DB_PATH = TEST_DB_DIR / "test.sqlite3"


@pytest.fixture(scope="session", autouse=True)
def test_database():
    # Create temp folder
    TEST_DB_DIR.mkdir(parents=True, exist_ok=True)

    # Point the app to the test DB (settings supports APP_DB_PATH)
    os.environ["APP_DB_PATH"] = str(TEST_DB_PATH)
    os.environ.setdefault("DB_ENGINE", "sqlite")
    os.environ.setdefault("ENV", "TEST")

    # Ensure a clean DB per test session
    try:
        if TEST_DB_PATH.exists():
            TEST_DB_PATH.unlink()
    except Exception:
        pass

    # Run migrations once per session from project root
    subprocess.check_call([sys.executable, str(ROOT / "migrate.py")])

    yield

    # Cleanup (comment out to keep DB for inspection)
    try:
        if TEST_DB_PATH.exists():
            TEST_DB_PATH.unlink()
        if TEST_DB_DIR.exists() and not any(TEST_DB_DIR.iterdir()):
            TEST_DB_DIR.rmdir()
    except Exception:
        pass


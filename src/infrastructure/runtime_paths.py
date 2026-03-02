import os
import sys
from pathlib import Path


APP_NAME = "my_OnCall_Manager"
DB_FILE_NAME = "my_oncall_manager.db"
LOG_FILE_NAME = "my_oncall_manager.log"
BOOKING_DATA_FOLDER = "data"
SEED_DB_FOLDER = "seed"


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def bundle_root() -> Path:
    if _is_frozen() and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return _project_root()


def executable_dir() -> Path:
    if _is_frozen():
        return Path(sys.executable).resolve().parent
    return _project_root()


def user_data_dir() -> Path:
    home = Path.home()
    if sys.platform == "darwin":
        base = home / "Library" / "Application Support"
    elif sys.platform.startswith("win"):
        appdata = os.getenv("APPDATA")
        base = Path(appdata) if appdata else home / "AppData" / "Roaming"
    else:
        base = home / ".local" / "share"

    app_dir = base / APP_NAME
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def db_file_path() -> Path:
    return user_data_dir() / DB_FILE_NAME


def log_file_path() -> Path:
    return user_data_dir() / LOG_FILE_NAME


def resource_path(*parts: str) -> Path:
    return bundle_root().joinpath(*parts)


def user_booking_data_dir() -> Path:
    documents_dir = Path.home() / "Documents"
    data_dir = documents_dir / APP_NAME / BOOKING_DATA_FOLDER
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def seed_db_path() -> Path | None:
    env_seed = os.getenv("MY_ONCALL_SEED_DB", "").strip()
    if env_seed:
        path = Path(env_seed).expanduser().resolve()
        return path if path.is_file() else None

    candidates = [
        resource_path(SEED_DB_FOLDER, DB_FILE_NAME),
        _project_root() / DB_FILE_NAME,
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def booking_csv_files() -> list[Path]:
    env_dir = os.getenv("MY_ONCALL_DATA_DIR")
    candidates = []
    if env_dir:
        candidates.append(Path(env_dir))

    candidates.extend(
        [
            user_booking_data_dir(),
            executable_dir() / BOOKING_DATA_FOLDER,
            user_data_dir() / BOOKING_DATA_FOLDER,
            bundle_root() / BOOKING_DATA_FOLDER,
            _project_root() / BOOKING_DATA_FOLDER,
        ]
    )

    seen: set[Path] = set()
    for directory in candidates:
        resolved = directory.expanduser().resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        if resolved.is_dir():
            files = sorted(resolved.glob("*.csv"))
            if files:
                return files

    fallback = user_booking_data_dir()
    return sorted(fallback.glob("*.csv"))

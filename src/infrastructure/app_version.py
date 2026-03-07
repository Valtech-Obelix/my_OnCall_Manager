import os
import subprocess
import sys
import plistlib
from pathlib import Path


def get_app_version() -> str:
    env_version = os.getenv("MY_ONCALL_MANAGER_VERSION") or os.getenv("APP_VERSION")
    if env_version and env_version.strip():
        return env_version.strip()

    plist_version = _get_bundled_plist_value("CFBundleShortVersionString")
    if plist_version:
        return plist_version

    version = _get_git_tag_version()
    if version:
        return version

    return "dev"


def _get_git_tag_version() -> str | None:
    project_root = Path(__file__).resolve().parents[2]
    git_command = [
        "git",
        "-C",
        str(project_root),
        "describe",
        "--tags",
        "--dirty",
        "--always",
    ]
    try:
        result = subprocess.run(
            git_command,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return None

    if result.returncode != 0:
        return None

    version = result.stdout.strip()
    return version or None


def get_app_build_info() -> dict[str, str]:
    version = get_app_version()
    commit = _run_git_command(["rev-parse", "HEAD"])
    build_date = _get_bundled_plist_value("MyOnCallManagerBuildDate")
    if not build_date:
        build_date = _run_git_command(
            ["log", "-1", "--pretty=format:%cd", "--date=iso-strict"]
        )
    if not commit:
        commit = _get_bundled_plist_value("MyOnCallManagerBuildCommit")

    info = {
        "version": version,
    }

    if commit:
        info["commit"] = commit
    if build_date:
        info["build_time"] = build_date

    return info


def _run_git_command(p_args: list[str]) -> str | None:
    project_root = Path(__file__).resolve().parents[2]
    command = [
        "git",
        "-C",
        str(project_root),
        *p_args,
    ]
    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return None

    if result.returncode != 0:
        return None

    value = result.stdout.strip()
    return value or None


def _get_bundled_plist_value(p_key: str) -> str | None:
    plist_path = _get_bundle_info_plist_path()
    if not plist_path:
        return None

    try:
        with plist_path.open("rb") as plist_file:
            payload = plistlib.load(plist_file)
    except (OSError, plistlib.InvalidFileException, ValueError):
        return None

    value = payload.get(p_key)
    if not value:
        return None
    return str(value).strip() or None


def _get_bundle_info_plist_path() -> Path | None:
    executable_path = Path(sys.executable or "")
    candidates = [
        executable_path.parent.parent / "Info.plist",
        executable_path.parent / "Info.plist",
    ]

    if hasattr(sys, "_MEIPASS"):
        candidates.insert(0, Path(sys._MEIPASS) / "Info.plist")

    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None

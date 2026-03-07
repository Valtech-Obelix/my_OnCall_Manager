import os
import subprocess
from pathlib import Path


def get_app_version() -> str:
    env_version = os.getenv("MY_ONCALL_MANAGER_VERSION") or os.getenv("APP_VERSION")
    if env_version and env_version.strip():
        return env_version.strip()

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
    build_date = _run_git_command(["log", "-1", "--pretty=format:%cd", "--date=iso-strict"])

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

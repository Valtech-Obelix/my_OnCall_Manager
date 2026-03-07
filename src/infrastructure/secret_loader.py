import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Callable

from src.infrastructure.runtime_paths import (
    opsgenie_config_example_path,
    opsgenie_config_path,
)


OPS_GENIE_CONFIG_SECTION = "opsgenie"
OPS_GENIE_CONFIG_KEY = "api_key_reference"


def load_opsgenie_api_key(
    p_logger_warning: Callable[[str], None] | None = None,
) -> str | None:
    op_ref = _load_opsgenie_api_key_ref(p_logger_warning)

    if not op_ref:
        return None

    op_binary = _resolve_op_executable(p_logger_warning)
    if op_binary is None:
        if p_logger_warning:
            p_logger_warning(
                "1Password CLI (op) nicht gefunden. "
                "OpsGenie API-Key kann nicht aus 1Password geladen werden."
            )
        return None

    op_env = os.environ.copy()
    extra_paths = "/opt/homebrew/bin:/usr/local/bin"
    existing_path = op_env.get("PATH", "")
    op_env["PATH"] = f"{extra_paths}:{existing_path}" if existing_path else extra_paths

    try:
        result = subprocess.run(
            [op_binary, "read", op_ref],
            check=True,
            capture_output=True,
            text=True,
            env=op_env,
        )
    except subprocess.CalledProcessError as ex:
        if p_logger_warning:
            p_logger_warning(
                "OpsGenie API-Key konnte nicht aus 1Password gelesen werden. "
                f"Bitte 1Password-Sitzung und Referenz prüfen. ({(ex.stderr or '').strip()})"
            )
        return None

    key = result.stdout.strip()
    return key or None


def _resolve_op_executable(
    p_logger_warning: Callable[[str], None] | None = None,
) -> str | None:
    candidates = [
        "/opt/homebrew/bin/op",
        "/usr/local/bin/op",
        "/usr/bin/op",
        "/bin/op",
    ]
    for candidate in candidates:
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate

    env = os.environ.get("PATH", "")
    op_binary = shutil.which("op", path=env)
    if p_logger_warning and op_binary is None:
        p_logger_warning(
            "1Password CLI wurde in PATH nicht gefunden. "
            f"Pfad gesucht in: {env or '<leer>'}"
        )
    return op_binary


def _load_opsgenie_api_key_ref(
    p_logger_warning: Callable[[str], None] | None = None,
) -> str | None:
    config_path = opsgenie_config_path()
    config = _load_config_payload(config_path, p_logger_warning)
    if config is None:
        example_config_path = opsgenie_config_example_path()
        if not example_config_path.exists():
            if p_logger_warning:
                p_logger_warning(
                    f"OpsGenie Config fehlt: {config_path}. "
                    "Bitte Referenz in der Config-Datei hinterlegen."
                )
            return None

        config = _load_config_payload(example_config_path, p_logger_warning)
    if config is None:
        return None

    ref = _extract_opsgenie_ref(config)
    if not ref:
        if p_logger_warning:
            p_logger_warning(
                "Keine 1Password-Referenz in der OpsGenie Config gefunden. "
                f"Erwartet: '{OPS_GENIE_CONFIG_SECTION}.{OPS_GENIE_CONFIG_KEY}'"
            )
        return None
    return ref


def _load_config_payload(
    p_config_path: Path,
    p_logger_warning: Callable[[str], None] | None = None,
) -> dict | None:
    return _read_config(p_config_path, p_logger_warning)


def _read_config(
    p_config_path: Path,
    p_logger_warning: Callable[[str], None] | None = None,
) -> dict | None:
    try:
        with p_config_path.open("r", encoding="utf-8") as config_file:
            payload = json.load(config_file)
    except OSError as err:
        if p_logger_warning:
            p_logger_warning(f"OpsGenie Config konnte nicht gelesen werden: {err}")
        return None
    except json.JSONDecodeError as err:
        if p_logger_warning:
            p_logger_warning(f"OpsGenie Config ist kein valides JSON: {err}")
        return None

    if not isinstance(payload, dict):
        if p_logger_warning:
            p_logger_warning("OpsGenie Config muss ein JSON-Objekt sein.")
        return None
    return payload


def _extract_opsgenie_ref(p_config: dict) -> str | None:
    section = p_config.get(OPS_GENIE_CONFIG_SECTION)
    if isinstance(section, dict):
        ref = section.get(OPS_GENIE_CONFIG_KEY)
        if isinstance(ref, str):
            normalized = ref.strip()
            if normalized and not normalized.startswith("<") and not normalized.endswith(">"):
                return normalized

    fallback_ref = (
        p_config.get("opsgenie_api_key_ref")
        or p_config.get("opsgenie_api_key_reference")
    )
    if isinstance(fallback_ref, str):
        normalized = fallback_ref.strip()
        if normalized and not normalized.startswith("<") and not normalized.endswith(">"):
            return normalized

    return None

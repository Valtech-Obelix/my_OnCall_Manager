import os
import shutil
import subprocess
from typing import Callable


OPS_GENIE_API_KEY_ENV = "OPS_GENIE_API_KEY"
OPS_GENIE_OP_REF_ENV = "OPS_GENIE_API_KEY_OP_REF"


def load_opsgenie_api_key(
    p_logger_warning: Callable[[str], None] | None = None,
) -> str | None:
    direct_value = os.getenv(OPS_GENIE_API_KEY_ENV, "").strip()
    if direct_value:
        return direct_value

    op_ref = os.getenv(OPS_GENIE_OP_REF_ENV, "").strip()
    if not op_ref:
        return None

    if shutil.which("op") is None:
        if p_logger_warning:
            p_logger_warning(
                "1Password CLI (op) nicht gefunden. "
                f"{OPS_GENIE_OP_REF_ENV} kann nicht aufgeloest werden."
            )
        return None

    try:
        result = subprocess.run(
            ["op", "read", op_ref],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        if p_logger_warning:
            p_logger_warning(
                "OpsGenie API-Key konnte nicht aus 1Password gelesen werden. "
                "Bitte op-Anmeldung/Referenz pruefen."
            )
        return None

    key = result.stdout.strip()
    return key or None

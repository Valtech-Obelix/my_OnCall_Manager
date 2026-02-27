import   logging
from     pathlib                                           import Path


LOG_FILE_NAME = "my_oncall_manager.log"


def setup_logging():

    log_file = Path(LOG_FILE_NAME)

    # Root-Logger holen
    logger = logging.getLogger()
    if getattr(logger, "_my_oncall_logging_configured", False):
        return

    logger.setLevel(logging.DEBUG)

    # Formatter
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    )

    console_formatter = logging.Formatter(
        "[%(levelname)s] %(message)s"
    )

    # File-Handler (DEBUG und höher)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    # Console-Handler (INFO und höher)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger._my_oncall_logging_configured = True

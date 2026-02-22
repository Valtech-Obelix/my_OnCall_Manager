import logging
from pathlib import Path


LOG_FILE_NAME = "my_oncall_manager.log"


def setup_logging():

    log_file = Path(LOG_FILE_NAME)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
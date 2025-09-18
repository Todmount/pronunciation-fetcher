import logging, os, sys

from logging.handlers import RotatingFileHandler
from rich.logging import RichHandler
from pathlib import Path


CONSOLE_FORMATTER = logging.Formatter("%(message)s")
FILE_FORMATTER = logging.Formatter('%(asctime)s | %(levelname)-8s | %(name)-8s | %(message)s')


def setup_logger(
        name: str,
        log_name_dir: Path,
        log_file_name: str = 'main.log',
        max_bytes: int = 5*1024*1024,
        backup_count: int = 3
):
    """Setup logger with rich console and file handlers."""
    if log_file_name.split('.')[-1]:
        raise ValueError("Incorrect log file extension, please check your 'setup_logger'")
    # Get the main logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Set the logger level to INFO


    if not logger.handlers:
        console_handler = RichHandler(
            show_time=False,
            show_level=True,
            show_path=False,
            rich_tracebacks=True
        )
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(CONSOLE_FORMATTER)
        logger.addHandler(console_handler)

        log_name_dir.mkdir(parents=True, exist_ok=True)
        log_file_path = log_name_dir / log_file_name

        file_handler = RotatingFileHandler(
            filename=log_file_path,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(FILE_FORMATTER)
        logger.addHandler(file_handler)

    # Add startup marker
    logger.debug("=" * 50)
    logger.debug("NEW APPLICATION INSTANCE STARTED")
    logger.debug(f"PID: {os.getpid()} | Python: {sys.version.split()[0]}")
    logger.debug("=" * 50)

    return logger


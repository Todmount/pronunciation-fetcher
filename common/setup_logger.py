import logging, os, sys

from logging.handlers import RotatingFileHandler
from rich.logging import RichHandler
from pathlib import Path


CONSOLE_FORMATTER = logging.Formatter("%(message)s")
FILE_FORMATTER = logging.Formatter('%(asctime)s | %(levelname)-8s | %(name)-28s | %(message)s')


def setup_logger(
        name: str,
        log_file_dir: Path,
        log_file_name: str = 'main.log',
        max_bytes: int = 5*1024*1024,
        backup_count: int = 3,
        is_main: bool = False
):
    """Setup logger with rich console and file handlers"""
    log_file_name = Path(log_file_name)
    log_ext = log_file_name.suffix
    if log_ext != '.log':
        raise ValueError(f"Incorrect log file extension, please check your 'setup_logger'. Your current is {log_ext}")
    # Get the main logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)


    if not logger.handlers:
        console_handler = RichHandler(
            show_time=False,
            show_level=False,
            show_path=False,
            rich_tracebacks=True
        )
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(CONSOLE_FORMATTER)
        logger.addHandler(console_handler)

        log_file_dir.mkdir(parents=True, exist_ok=True)
        log_file_path = log_file_dir / log_file_name

        file_handler = RotatingFileHandler(
            filename=log_file_path,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(FILE_FORMATTER)
        logger.addHandler(file_handler)

    if is_main:
        # Add startup marker
        logger.debug("=" * 50)
        logger.debug("NEW APPLICATION INSTANCE STARTED")
        logger.debug(f"PID: {os.getpid()} | Python: {sys.version.split()[0]}")
        logger.debug("=" * 50)

    return logger


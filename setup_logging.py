import os
from logging import (
    getLogger,
    Formatter,
    StreamHandler,
    DEBUG,
    INFO,
)
from logging.handlers import RotatingFileHandler


def setup_logging(debug=False):
    NAME = "gemini-trader"
    FORMAT = "%(asctime)s %(levelname)s: %(message)s"
    VERBOSE_FORMAT = (
        "(%(name)s) %(asctime)s %(module)s %(levelname)s: %(message)s"
    )
    FILENAME = f"logs/gemini-trader.log"
    VERBOSE_FILE = f"logs/verbose_gemini-trader.log"
    MAX_BYTES =  500 * 1024
    BACKUP_COUNT = 5

    def create_logs_directory():
        if not os.path.isdir("logs"):
            os.mkdir("logs")

    def setup_logger():
        logger.setLevel(DEBUG)

    def setup_stream_handler():
        log_formatter = Formatter(FORMAT)
        log_stream_handler = StreamHandler()
        log_stream_handler.setFormatter(log_formatter)
        log_stream_handler.setLevel(DEBUG)
        logger.addHandler(log_stream_handler)

    def setup_file_handler():
        log_formatter = Formatter(FORMAT)
        log_file_handler = RotatingFileHandler(
            FILENAME, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT
        )
        log_file_handler.setFormatter(log_formatter)
        log_file_handler.setLevel(INFO)
        logger.addHandler(log_file_handler)

    def setup_verbose_file_handler():
        verbose_log_formatter = Formatter(FORMAT)
        verbose_log_file_handler = RotatingFileHandler(
            VERBOSE_FILE, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT
        )
        verbose_log_file_handler.setFormatter(verbose_log_formatter)
        verbose_log_file_handler.setLevel(DEBUG)
        logger.addHandler(verbose_log_file_handler)

    logger = getLogger(NAME)

    create_logs_directory()

    setup_logger()

    if debug:
        setup_stream_handler()
    else:
        setup_file_handler()
        setup_verbose_file_handler()

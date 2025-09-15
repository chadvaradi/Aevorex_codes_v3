# backend/utils/logger_config.py
import logging
import sys
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler

# --- Defensive Guard against Circular Imports ---
# If this module is being imported, but it's already in sys.modules,
# it means we have a circular dependency. In that case, we can't fully
# set up our custom logger, but we can provide a basic fallback.
if "logger_config" in sys.modules:
    # Provide a basic logger function that falls back to the standard logging.
    def get_logger(name: str) -> logging.Logger:
        return logging.getLogger(name)
else:
    # --- Standard Configuration ---

    # Default values, now read from environment variables or fallback to these constants
    LOG_LEVEL_STR = os.environ.get("LOG_LEVEL", "INFO").upper()
    DEFAULT_LOG_FORMAT = (
        "%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s"
    )
    DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    LOG_DIR = os.environ.get("LOG_DIR", None)  # e.g., "logs/"
    MAX_LOG_FILE_BYTES = 10 * 1024 * 1024  # 10 MB
    LOG_FILE_BACKUP_COUNT = 5

    # Mapping from log level strings to logging constants
    LOG_LEVEL_MAP = {
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
    }

    # --- Main Logger Configuration Function ---

    def setup_logging():
        """
        Configures the application's logging system based on environment variables.
        This function is now self-contained and does not depend on the project's 'settings'.
        """
        internal_logger = logging.getLogger(
            "LoggerSetup"
        )  # Dedicated logger for the setup process

        # 1. Determine log level
        log_level = LOG_LEVEL_MAP.get(LOG_LEVEL_STR, logging.INFO)
        internal_logger.info(
            f"Configuring logging with level: {logging.getLevelName(log_level)} ({LOG_LEVEL_STR})"
        )

        # 2. Create formatter
        log_formatter = logging.Formatter(
            DEFAULT_LOG_FORMAT, datefmt=DEFAULT_DATE_FORMAT
        )

        # 3. Get root logger and clear existing handlers
        root_logger = logging.getLogger()
        if root_logger.hasHandlers():
            internal_logger.info(
                "Removing existing handlers from root logger to prevent duplicates."
            )
            for handler in root_logger.handlers[:]:
                try:
                    handler.close()
                    root_logger.removeHandler(handler)
                except Exception as e:
                    internal_logger.warning(
                        f"Could not close/remove handler {handler}: {e}"
                    )

        # 4. Set root logger level
        root_logger.setLevel(log_level)

        # 5. Add Console Handler (StreamHandler)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(log_formatter)
        console_handler.setLevel(
            logging.DEBUG
        )  # Console shows all levels from DEBUG up
        root_logger.addHandler(console_handler)
        internal_logger.info("Added StreamHandler to root logger for console output.")

        # 6. Add File Handler (RotatingFileHandler) if LOG_DIR is set
        if LOG_DIR:
            log_dir_path = Path(LOG_DIR)
            try:
                log_dir_path.mkdir(parents=True, exist_ok=True)
                log_file_path = log_dir_path / "aevorex_finbot_backend.log"

                file_handler = RotatingFileHandler(
                    filename=log_file_path,
                    maxBytes=MAX_LOG_FILE_BYTES,
                    backupCount=LOG_FILE_BACKUP_COUNT,
                    encoding="utf-8",
                )
                file_handler.setFormatter(log_formatter)
                file_handler.setLevel(logging.DEBUG)  # File also logs everything
                root_logger.addHandler(file_handler)
                internal_logger.info(
                    f"Added RotatingFileHandler. Log file: {log_file_path}"
                )
            except PermissionError:
                internal_logger.error(
                    f"Permission denied to write to log directory: {log_dir_path}",
                    exc_info=True,
                )
            except Exception as e:
                internal_logger.error(
                    f"Failed to create file handler for {log_dir_path}: {e}",
                    exc_info=True,
                )
        else:
            internal_logger.warning(
                "LOG_DIR environment variable not set. Skipping file logging."
            )

        # 7. Quiet down noisy third-party loggers
        noisy_loggers = [
            "httpx",
            "asyncio",
            "pandas_ta",
            "yfinance",
            "urllib3",
            "watchfiles",
        ]
        for logger_name in noisy_loggers:
            logging.getLogger(logger_name).setLevel(logging.WARNING)

        internal_logger.info(
            f"Logging setup complete. Root logger level: {logging.getLevelName(root_logger.level)}"
        )

    # --- Logger Instance Getter Function ---
    def get_logger(name: str) -> logging.Logger:
        """
        Retrieves a logger instance with the given name.
        The instance inherits settings from the root logger (level, handlers, format).
        """
        return logging.getLogger(name)

# To ensure logging is configured at least once when the module is imported
# You might want to call this from your application's entry point instead
# to have more control over when it happens.
# For now, let's call it here for simplicity, assuming this module is imported early.
# setup_logging()

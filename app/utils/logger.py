import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any


class FormatLog(logging.Formatter):
    """Custom formatter for structured logging in CloudWatch."""
    ICONS = {
        logging.DEBUG: "🐛",
        logging.INFO: "✅",
        logging.WARNING: "⚠️",
        logging.ERROR: "❌",
        logging.CRITICAL: "🔥"
    }

    def format(self, record):
        icon = self.ICONS.get(record.levelno, "ℹ️")  # default icon
        log_obj = {
            'level': f"{icon} {record.levelname}",
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'message': f"{icon} {record.getMessage()}",
            'function': record.funcName,
            'line': record.lineno,
            'module': record.module,
            'pathname': record.pathname
        }

        # Add extra data if present
        if hasattr(record, 'extra_data'):
            log_obj.update(record.extra_data)

        # Add exception info if present
        if record.exc_info:
            log_obj['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_obj, ensure_ascii=False)


def setup_logger(log_level: str = "INFO") -> logging.Logger:
    """
    Setup and configure logger with CloudWatch formatter.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("fastapi_app")

    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(numeric_level)

    # Clear existing handlers to avoid duplicates
    logger.handlers = []

    # Create handler with CloudWatch formatter
    handler = logging.StreamHandler()
    handler.setFormatter(FormatLog())
    logger.addHandler(handler)

    # Prevent propagation to avoid duplicate logs
    logger.propagate = False

    return logger


def log_with_extra(logger: logging.Logger, level: str, message: str, extra_data: Dict[str, Any] = None):
    """
    Log message with extra structured data.

    Args:
        logger: Logger instance
        level: Log level (debug, info, warning, error, critical)
        message: Log message
        extra_data: Additional data to include in log
    """
    if extra_data is None:
        extra_data = {}

    # Create a log record with extra data
    log_method = getattr(logger, level.lower())
    log_method(message, extra={"extra_data": extra_data})


# Create a default logger instance
logger = setup_logger()
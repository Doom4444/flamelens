import logging
import sys
from typing import Optional


def setup_logging(log_level: Optional[str] = "INFO") -> logging.Logger:
    """
    Configures application-wide structured console logging.
    """
    level_name = (log_level or "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    log_format = "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Configure root logger
    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt=date_format,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    app_logger = logging.getLogger("flamelens")
    app_logger.setLevel(level)
    return app_logger


logger = logging.getLogger("flamelens")

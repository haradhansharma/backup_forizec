import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.core.config import settings


LOG_DIR = Path(settings.BASE_DIR) / "logs"
LOG_DIR.mkdir(exist_ok = True)

LOG_FILE = LOG_DIR / "forizec.log"

def configure_logging():
    """
    Configure root logging for the poject.
    All Logger under `forizec` will inherit this configuration.
    """
    
    # Formatter    
    formatter = logging.Formatter(        
        fmt = "%(levelname)s | %(asctime)s | %(name)s | %(filename)s:%(lineno)d | %(message)s",
        datefmt = "%Y-%m-%d %H:%M:%S",
    )
    
    # console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    
    # Rotating file handler
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    # Root project logger
    root_logger =  logging.getLogger("forizec")
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Attach to uvicorn loggers (so uvicorn + forizec use same handler)
    uvicorn_logger = logging.getLogger("uvicorn")
    root_logger.handlers.extend(uvicorn_logger.handlers)

    return root_logger

def get_logger(name: str | None = None) -> logging.Logger:
    """
    Get a child logger for a specific module.
    Example get_logger("api") -> forizec.api
    """
    base_logger = logging.getLogger("forizec")
    if name:
        return base_logger.getChild(name)
    return base_logger
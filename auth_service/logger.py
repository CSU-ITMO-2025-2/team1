# logger.py
import logging
import os

DEFAULT_FMT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

def setup_logging(level: str | None = None, fmt: str = DEFAULT_FMT) -> None:
    """
    Простая инициализация логов.
    Вызывай один раз в самом начале приложения (до первых log.* вызовов).
    """
    lvl = (level or os.getenv("LOG_LEVEL", "INFO")).upper()
    logging.basicConfig(level=getattr(logging, lvl, logging.INFO), format=fmt)

    # Умеряем болтливость клиентов сети по умолчанию
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

def get_logger(name: str = "auth_bff") -> logging.Logger:
    """Возвращает именованный логгер приложения."""
    return logging.getLogger(name)
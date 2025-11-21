"""Логгер"""

import logging

from app.core.config import Config

# Уровни логирования
#     "CRITICAL": logging.CRITICAL
#     "ERROR": logging.ERROR
#     "WARNING": logging.WARNING
#     "INFO": logging.INFO
#     "DEBUG": logging.DEBUG
#     "NOTSET": logging.NOTSET


if Config.load():
    config = Config.load()
else:
    print("Конфиг не загружен")


def get_logger(name: str = "core.config") -> logging.Logger:
    """Вызывает логгер. Определяет откуда лог и уровень логирования."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
            ),
        )
        logger.addHandler(handler)
        logger.propagate = False  # не лить в root
    logger.setLevel(config.logging.level)
    return logger


if __name__ == "__main__":
    log = get_logger(__name__)
    log.debug("DEBUG: диагностическое сообщение")

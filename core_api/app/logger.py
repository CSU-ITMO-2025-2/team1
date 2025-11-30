"""
Унифицированный логгер для всех компонентов сервиса Core API
"""

import logging
import sys
import os


def setup_logger(name: str = None, level: int = None) -> logging.Logger:
    """
    Создаёт логгер с именем модуля и настраивает вывод.
    Если name не указан — используется __name__ вызывающего модуля.
    """
    # Если имя не передано, используем имя вызывающего модуля
    logger_name = name or __name__

    logger = logging.getLogger(logger_name)
    if logger.handlers:
        return logger  # избегаем дублирования обработчиков

    # Уровень логирования
    log_level = level or getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper())

    logger.setLevel(log_level)

    # Формат: УРОВЕНЬ | МОДУЛЬ | СООБЩЕНИЕ
    formatter = logging.Formatter(
        fmt="%(levelname)-8s | %(name)s | %(message)s",
        datefmt=None
    )

    # Обработчик для stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

"""
Унифицированный логгер для всех компонентов HR-ассистента

Модуль предоставляет единый интерфейс логирования, который:
1. Обеспечивает консистентный формат логов во всех сервисах
2. Поддерживает настройку уровня логирования через переменные окружения
3. Предотвращает дублирование обработчиков логов
4. Выводит логи в stdout в формате: УРОВЕНЬ | МОДУЛЬ | СООБЩЕНИЕ

Использование:
    logger = setup_logger(__name__)
    logger.info("Сообщение", extra={"дополнительное_поле": "значение"})
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

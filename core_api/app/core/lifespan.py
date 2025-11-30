"""Управление жизненным циклом приложения."""

from contextlib import asynccontextmanager

from app.api.dependencies import set_rabbit_client
from app.core.config import settings
from app.db import init_db
from app.db.session import close_db
from app.logger import setup_logger
from app.rabbitmq import RabbitMQClient
from fastapi import FastAPI

logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения.

    Выполняет:
    - При запуске: инициализация БД и RabbitMQ
    - При завершении: корректное закрытие соединений

    Args:
        app: Экземпляр FastAPI приложения
    """
    # ========== STARTUP ==========
    logger.info("Запуск Core API")

    # Инициализация БД
    try:
        init_db()
        logger.info("База данных успешно инициализирована")
    except Exception as e:
        logger.error(
            "Ошибка при инициализации БД", extra={"error": str(e)}, exc_info=True
        )

    # Инициализация RabbitMQ
    rabbit_client = None
    try:
        logger.info("Инициализация клиента RabbitMQ")
        rabbit_client = RabbitMQClient(settings.rabbitmq.url)
        await rabbit_client.connect()
        set_rabbit_client(rabbit_client)
        logger.info("RabbitMQ клиент успешно инициализирован")
    except Exception as e:
        logger.error(
            "Ошибка при инициализации RabbitMQ", extra={"error": str(e)}, exc_info=True
        )
        raise  # останавливаем запуск

    # Приложение работает
    yield

    # ========== SHUTDOWN ==========
    logger.info("Завершение работы Core API")

    # Закрытие подключения к БД
    try:
        await close_db()
        logger.info("Соединение с БД закрыто")
    except Exception as e:
        logger.error("Ошибка при закрытии БД", extra={"error": str(e)}, exc_info=True)

    # Закрытие RabbitMQ
    if rabbit_client:
        try:
            await rabbit_client.close()
            logger.info("Соединение с RabbitMQ закрыто")
        except Exception as e:
            logger.error(
                "Ошибка при закрытии RabbitMQ", extra={"error": str(e)}, exc_info=True
            )

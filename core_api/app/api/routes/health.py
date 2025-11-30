"""Роуты для проверки работоспособности."""

import time

from fastapi import APIRouter, Depends
from app.logger import setup_logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db_session, get_rabbit_client
from app.api.schemas.health_check import HealthResponse
from app.rabbitmq import RabbitMQClient

router = APIRouter(tags=["Health"])
logger = setup_logger(__name__)


@router.get("/health", response_model=HealthResponse)
async def health_check(
    rabbit_client: RabbitMQClient = Depends(get_rabbit_client),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Проверка работоспособности сервиса.

    Проверяет:
    - Доступность сервиса
    - Статус подключения к RabbitMQ
    - Статус подключения к PostgreSQL

    Returns:
        HealthResponse: Статус работоспособности
    """
    # Проверяем подключение к RabbitMQ
    if (
        rabbit_client
        and rabbit_client.connection
        and not rabbit_client.connection.is_closed
    ):
        rabbit_status = "подключен"
    else:
        rabbit_status = "отключен"

    # Проверяем подключение к БД
    try:
        await session.execute(text("SELECT 1"))
        db_status = "подключена"
    except Exception as e:
        logger.error("Ошибка подключения к БД", extra={"error": str(e)}, exc_info=True)
        db_status = "отключена"

    logger.info(
        "Проверка работоспособности сервиса",
        extra={
            "rabbitmq_статус": rabbit_status,
            "db_статус": db_status,
            "время_проверки": time.strftime("%Y-%m-%d %H:%M:%S"),
        },
    )

    return HealthResponse(
        status="healthy", rabbitmq_status=rabbit_status, db_status=db_status
    )

"""Роуты для генерации описаний вакансий."""

import time
from typing import Optional

from fastapi import APIRouter, Depends

from app.api.dependencies import (
    get_generation_service,
    get_logging_service,
    get_user_data,
    get_user_service,
)
from app.api.schemas.common import UserData
from app.api.schemas.job_description import (
    JobDescriptionRequest,
    JobDescriptionResponse,
)
from app.logger import setup_logger
from app.services.generation_service import GenerationService
from app.services.logging_service import LoggingService
from app.services.user_service import UserService

router = APIRouter(prefix="/job_description", tags=["Job Description"])
logger = setup_logger(__name__)


@router.post("/generate", response_model=JobDescriptionResponse)
async def generate_job_description(
    request: JobDescriptionRequest,
    user_service: UserService = Depends(get_user_service),
    generation_service: GenerationService = Depends(get_generation_service),
    logging_service: LoggingService = Depends(get_logging_service),
    user_data: Optional[UserData] = Depends(get_user_data),
):
    """
    Сгенерировать описание вакансии.

    Args:
        request: Запрос с входными данными
        user_service: Сервис работы с пользователями
        generation_service: Сервис генерации
        logging_service: Сервис логирования
        user_data: Данные пользователя из cookie (опционально)

    Returns:
        JobDescriptionResponse: Сгенерированное описание вакансии
    """
    start_time = time.time()
    user_id = None

    try:
        logger.info(
            "Начало генерации описания вакансии",
            extra={"input_length": len(request.input_data)},
        )

        # Получаем или создаём пользователя
        if user_data:
            user_id = await user_service.get_or_create_user(
                email=user_data.email, full_name=user_data.full_name
            )

        # Генерируем результат
        result = await generation_service.generate_job_description(request.input_data)

        # Логируем успех
        latency_ms = int((time.time() - start_time) * 1000)
        await logging_service.log_success(
            request_type="job_description",
            user_id=user_id,
            request_payload={
                "input_data": request.input_data,
            },
            response_payload=result,
            latency_ms=latency_ms,
        )

        logger.info(
            "Успешная генерация описания вакансии", extra={"latency_ms": latency_ms}
        )

        return result

    except Exception as e:
        # Логируем ошибку
        latency_ms = int((time.time() - start_time) * 1000)
        await logging_service.log_error(
            request_type="job_description",
            user_id=user_id,
            error_message=str(e),
            latency_ms=latency_ms,
        )

        logger.error(
            "Ошибка при генерации описания вакансии",
            extra={"error_type": type(e).__name__, "message": str(e)},
            exc_info=True,
        )

        raise

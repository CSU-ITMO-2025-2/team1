"""Роуты для оценки резюме."""

import time
from typing import Optional

from fastapi import APIRouter, Depends

from app.api.dependencies import (
    get_generation_service,
    get_logging_service,
    get_user_service,
    get_user_data,
)
from app.api.schemas.resume import ResumeEvaluationRequest, ResumeEvaluationResponse
from app.api.schemas.common import UserData
from app.logger import setup_logger
from app.services.generation_service import GenerationService
from app.services.logging_service import LoggingService
from app.services.user_service import UserService

router = APIRouter(prefix="/resume", tags=["Resume Evaluation"])
logger = setup_logger(__name__)


@router.post("/evaluation", response_model=ResumeEvaluationResponse)
async def evaluate_resume(
    request: ResumeEvaluationRequest,
    user_service: UserService = Depends(get_user_service),
    generation_service: GenerationService = Depends(get_generation_service),
    logging_service: LoggingService = Depends(get_logging_service),
    user_data: Optional[UserData] = Depends(get_user_data),
):
    """
    Оценить соответствие резюме вакансии.

    Принимает текстовые данные вакансии и резюме.
    Frontend должен предварительно извлечь текст из файлов.

    Args:
        request: Запрос с текстами вакансии и резюме
        user_service: Сервис работы с пользователями
        generation_service: Сервис генерации
        logging_service: Сервис логирования
        user_data: Данные пользователя из cookie (опционально)

    Returns:
        ResumeEvaluationResponse: Результат оценки соответствия
    """
    start_time = time.time()
    user_id = None

    try:
        logger.info(
            "Начало обработки оценки резюме",
            extra={
                "vacancy_length": len(request.vacancy_text),
                "resume_length": len(request.resume_text),
            },
        )

        # Получаем или создаём пользователя
        if user_data:
            user_id = await user_service.get_or_create_user(
                email=user_data.email,
                full_name=user_data.full_name,
            )

        # Генерируем результат
        result = await generation_service.evaluate_resume(
            request.vacancy_text, request.resume_text
        )

        # Логируем успех
        latency_ms = int((time.time() - start_time) * 1000)
        await logging_service.log_success(
            request_type="resume_evaluation",
            user_id=user_id,
            request_payload={
                "vacancy_text": request.vacancy_text,
                "resume_text": request.resume_text,
            },
            response_payload=result,
            latency_ms=latency_ms,
        )

        logger.info(
            "Успешная обработка оценки резюме", extra={"latency_ms": latency_ms}
        )

        return result

    except Exception as e:
        # Логируем ошибку
        latency_ms = int((time.time() - start_time) * 1000)
        await logging_service.log_error(
            request_type="resume_evaluation",
            user_id=user_id,
            error_message=str(e),
            latency_ms=latency_ms,
        )

        logger.error(
            "Ошибка при обработке оценки резюме",
            extra={"error_type": type(e).__name__, "message": str(e)},
            exc_info=True,
        )

        # Перебрасываем исключение для обработки middleware
        raise

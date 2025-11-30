"""Роуты для генерации вопросов для интервью."""
import time
from typing import Optional
from fastapi import APIRouter, Depends
from app.api.dependencies import (
    get_user_service,
    get_generation_service,
    get_logging_service,
    get_user_data,
)
from app.services.user_service import UserService
from app.services.generation_service import GenerationService
from app.services.logging_service import LoggingService
from app.api.schemas.questions import QuestionGenerationRequest, QuestionGenerationResponse
from app.api.schemas.common import UserData
from app.logger import setup_logger

router = APIRouter(prefix="/questions", tags=["Question Generation"])
logger = setup_logger(__name__)


@router.post("/generate", response_model=QuestionGenerationResponse)
async def generate_questions(
    request: QuestionGenerationRequest,
    user_service: UserService = Depends(get_user_service),
    generation_service: GenerationService = Depends(get_generation_service),
    logging_service: LoggingService = Depends(get_logging_service),
    user_data: Optional[UserData] = Depends(get_user_data),
):
    """
    Сгенерировать вопросы для интервью на основе вакансии и резюме.
    
    Принимает текстовые данные вакансии и резюме.
    Frontend должен предварительно извлечь текст из файлов.
    
    Шаги:
    1. Получаем тексты вакансии и резюме
    2. Вызываем пайплайн оценки соответствия и получаем report
    3. Передаём report + исходные тексты в очередь генерации вопросов
    
    Args:
        request: Запрос с текстами вакансии и резюме
        user_service: Сервис работы с пользователями
        generation_service: Сервис генерации
        logging_service: Сервис логирования
        user_data: Данные пользователя из cookie (опционально)
        
    Returns:
        QuestionGenerationResponse: Сгенерированные вопросы для интервью
    """
    start_time = time.time()
    user_id = None
    
    try:
        logger.info(
            "Начало генерации вопросов по вакансии и резюме",
            extra={
                "vacancy_length": len(request.vacancy_text),
                "resume_length": len(request.resume_text),
            }
        )
        
        # Получаем или создаём пользователя
        if user_data:
            user_id = await user_service.get_or_create_user(
                email=user_data.email,
                full_name=user_data.full_name
            )
        
        # Шаг 1: Оценка соответствия резюме
        logger.debug("Отправка данных в очередь оценки резюме")
        evaluation_report = await generation_service.evaluate_resume(
            request.vacancy_text,
            request.resume_text
        )
        
        # Шаг 2: Генерация вопросов на основе report
        logger.debug("Отправка данных в очередь генерации вопросов")
        result = await generation_service.generate_questions(
            request.vacancy_text,
            request.resume_text,
            evaluation_report
        )
        
        # Логируем успех
        latency_ms = int((time.time() - start_time) * 1000)
        await logging_service.log_success(
            request_type="question_generation",
            user_id=user_id,
            request_payload={
                "vacancy_text": request.vacancy_text,
                "resume_text": request.resume_text,
            },
            response_payload=result,
            latency_ms=latency_ms
        )
        
        logger.info(
            "Успешная генерация вопросов",
            extra={"latency_ms": latency_ms}
        )
        
        return result
    
    except Exception as e:
        # Логируем ошибку
        latency_ms = int((time.time() - start_time) * 1000)
        await logging_service.log_error(
            request_type="question_generation",
            user_id=user_id,
            error_message=str(e),
            latency_ms=latency_ms
        )
        
        logger.error(
            "Ошибка при генерации вопросов",
            extra={"error_type": type(e).__name__, "message": str(e)},
            exc_info=True
        )
        
        # Перебрасываем исключение для обработки middleware
        raise

"""Сервис логирования результатов генераций."""
from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import GenerationResultRepository
from app.logger import setup_logger

logger = setup_logger(__name__)


class LoggingService:
    """Сервис логирования результатов в БД."""
    
    def __init__(self, session: AsyncSession):
        """
        Инициализация сервиса.
        
        Args:
            session: Async сессия SQLAlchemy
        """
        self.session = session
        self.gen_repo = GenerationResultRepository(session)
    
    async def log_success(
        self,
        request_type: str,
        user_id: Optional[int],
        request_payload: Dict[str, Any],
        response_payload: Any,
        latency_ms: int
    ) -> None:
        """
        Залогировать успешный результат.
        
        Args:
            request_type: Тип запроса (resume_evaluation, job_description, etc.)
            user_id: ID пользователя (опционально)
            request_payload: Входные данные запроса
            response_payload: Результат генерации
            latency_ms: Время выполнения в миллисекундах
        """
        try:
            # Преобразуем response_payload в dict если это не dict
            if not isinstance(response_payload, dict):
                response_payload = {"result": str(response_payload)}
            
            await self.gen_repo.create(
                request_type=request_type,
                status="success",
                user_id=user_id,
                request_payload=request_payload,
                response_payload=response_payload,
                latency_ms=latency_ms
            )
            
            logger.debug(
                "Результат успешно сохранен в БД",
                extra={
                    "request_type": request_type,
                    "user_id": user_id,
                    "latency_ms": latency_ms
                }
            )
        
        except Exception as e:
            logger.error(
                "Ошибка при сохранении результата в БД",
                extra={
                    "request_type": request_type,
                    "error": str(e)
                },
                exc_info=True
            )
    
    async def log_error(
        self,
        request_type: str,
        user_id: Optional[int],
        error_message: str,
        latency_ms: int,
        request_payload: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Залогировать ошибку.
        
        Args:
            request_type: Тип запроса
            user_id: ID пользователя (опционально)
            error_message: Сообщение об ошибке
            latency_ms: Время выполнения в миллисекундах
            request_payload: Входные данные запроса (опционально)
        """
        try:
            await self.gen_repo.create(
                request_type=request_type,
                status="error",
                user_id=user_id,
                error_message=error_message,
                latency_ms=latency_ms,
                request_payload=request_payload
            )
            
            logger.debug(
                "Ошибка успешно сохранена в БД",
                extra={
                    "request_type": request_type,
                    "user_id": user_id,
                    "latency_ms": latency_ms
                }
            )
        
        except Exception as e:
            logger.error(
                "Ошибка при сохранении ошибки в БД",
                extra={
                    "request_type": request_type,
                    "error": str(e)
                },
                exc_info=True
            )


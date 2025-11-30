"""
Репозиторий для работы с результатами генераций.

Реализует операции CRUD для модели GenerationResult.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import GenerationResult
from app.logger import setup_logger

# Логгер для модуля
logger = setup_logger(__name__)


class GenerationResultRepository:
    """
    Репозиторий для работы с результатами генераций.
    
    Предоставляет методы для сохранения и поиска результатов
    работы LLM/ML воркеров.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Инициализация репозитория.
        
        Args:
            session: Async сессия SQLAlchemy
        """
        self.session = session
    
    async def get_by_id(self, result_id: int) -> Optional[GenerationResult]:
        """
        Получить результат генерации по ID.
        
        Args:
            result_id: Идентификатор результата
            
        Returns:
            GenerationResult | None: Найденный результат или None
        """
        result = await self.session.execute(
            select(GenerationResult).where(GenerationResult.id == result_id)
        )
        return result.scalar_one_or_none()
    
    async def create(
        self,
        request_type: str,
        status: str = "success",
        user_id: Optional[int] = None,
        request_payload: Optional[dict] = None,
        response_payload: Optional[dict] = None,
        error_message: Optional[str] = None,
        latency_ms: Optional[int] = None,
    ) -> GenerationResult:
        """
        Создать запись о результате генерации.
        
        Args:
            request_type: Тип запроса (job_description, resume_evaluation, etc.)
            status: Статус выполнения (success, error, timeout)
            user_id: ID пользователя (опционально)
            request_payload: Входные данные запроса
            response_payload: Результат генерации
            error_message: Сообщение об ошибке
            latency_ms: Время выполнения в мс
            
        Returns:
            GenerationResult: Созданная запись
        """
        result = GenerationResult(
            user_id=user_id,
            request_type=request_type,
            request_payload=request_payload,
            response_payload=response_payload,
            status=status,
            error_message=error_message,
            latency_ms=latency_ms,
        )
        
        self.session.add(result)
        await self.session.commit()
        await self.session.refresh(result)
        
        logger.info(
            "Сохранён результат генерации",
            extra={
                "result_id": result.id,
                "request_type": request_type,
                "user_id": user_id,
                "status": status,
                "latency_ms": latency_ms
            }
        )
        
        return result
    
    async def get_by_user_id(
        self,
        user_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> list[GenerationResult]:
        """
        Получить результаты генераций пользователя.
        
        Args:
            user_id: ID пользователя
            limit: Максимальное количество записей
            offset: Смещение для пагинации
            
        Returns:
            list[GenerationResult]: Список результатов генераций
        """
        result = await self.session.execute(
            select(GenerationResult)
            .where(GenerationResult.user_id == user_id)
            .order_by(GenerationResult.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
    
    async def get_by_request_type(
        self,
        request_type: str,
        limit: int = 100,
        offset: int = 0
    ) -> list[GenerationResult]:
        """
        Получить результаты генераций по типу запроса.
        
        Args:
            request_type: Тип запроса
            limit: Максимальное количество записей
            offset: Смещение для пагинации
            
        Returns:
            list[GenerationResult]: Список результатов генераций
        """
        result = await self.session.execute(
            select(GenerationResult)
            .where(GenerationResult.request_type == request_type)
            .order_by(GenerationResult.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
    
    async def get_by_user_and_type(
        self,
        user_id: int,
        request_type: str,
        limit: int = 100,
        offset: int = 0
    ) -> list[GenerationResult]:
        """
        Получить результаты генераций пользователя по типу запроса.
        
        Args:
            user_id: ID пользователя
            request_type: Тип запроса
            limit: Максимальное количество записей
            offset: Смещение для пагинации
            
        Returns:
            list[GenerationResult]: Список результатов генераций
        """
        result = await self.session.execute(
            select(GenerationResult)
            .where(
                GenerationResult.user_id == user_id,
                GenerationResult.request_type == request_type
            )
            .order_by(GenerationResult.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
    
    async def get_statistics_by_user(
        self,
        user_id: int
    ) -> dict[str, int]:
        """
        Получить статистику генераций пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            dict: Словарь со статистикой по типам запросов
        """
        from sqlalchemy import func
        
        result = await self.session.execute(
            select(
                GenerationResult.request_type,
                func.count(GenerationResult.id).label("count")
            )
            .where(GenerationResult.user_id == user_id)
            .group_by(GenerationResult.request_type)
        )
        
        stats = {row.request_type: row.count for row in result}
        
        return stats


"""Сервис для работы с пользователями."""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import UserRepository
from app.logger import setup_logger

logger = setup_logger(__name__)


class UserService:
    """Сервис управления пользователями."""
    
    def __init__(self, session: AsyncSession):
        """
        Инициализация сервиса.
        
        Args:
            session: Async сессия SQLAlchemy
        """
        self.session = session
        self.user_repo = UserRepository(session)
    
    async def get_or_create_user(
        self,
        email: str,
        full_name: str
    ) -> Optional[int]:
        """
        Получить или создать пользователя и вернуть его ID.
        
        Использует email как уникальный идентификатор.
        
        Args:
            email: Email пользователя
            full_name: Полное имя пользователя
            
        Returns:
            Optional[int]: ID пользователя или None при ошибке
        """
        try:
            user, created = await self.user_repo.get_or_create_by_email(
                email=email,
                full_name=full_name,
            )
            
            if created:
                logger.info(
                    "Создан новый пользователь",
                    extra={
                        "user_id": user.id,
                        "email": email
                    }
                )
            else:
                logger.debug(
                    "Найден существующий пользователь",
                    extra={"user_id": user.id}
                )
            
            return user.id
        
        except Exception as e:
            logger.error(
                "Ошибка при работе с пользователем в БД",
                extra={"error": str(e)},
                exc_info=True
            )
            return None


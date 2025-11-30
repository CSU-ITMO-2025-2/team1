"""
Репозиторий для работы с пользователями.

Реализует операции CRUD для модели User.
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.logger import setup_logger

# Логгер для модуля
logger = setup_logger(__name__)


class UserRepository:
    """
    Репозиторий для работы с пользователями.
    
    Предоставляет методы для создания и поиска пользователей в БД.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Инициализация репозитория.
        
        Args:
            session: Async сессия SQLAlchemy
        """
        self.session = session
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Получить пользователя по ID.
        
        Args:
            user_id: Идентификатор пользователя
            
        Returns:
            User | None: Найденный пользователь или None
        """
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Получить пользователя по email.
        
        Args:
            email: Email пользователя
            
        Returns:
            User | None: Найденный пользователь или None
        """
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def create(
        self,
        email: str,
        full_name: str
    ) -> User:
        """
        Создать нового пользователя.
        
        Args:
            email: Email пользователя (уникальный)
            full_name: Полное имя пользователя
            
        Returns:
            User: Созданный пользователь
        """
        user = User(
            email=email,
            full_name=full_name
        )
        
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        
        logger.info(
            "Создан новый пользователь",
            extra={
                "user_id": user.id,
                "email": email
            }
        )
        
        return user
    
    async def get_or_create_by_email(
        self,
        email: str,
        full_name: str
    ) -> tuple[User, bool]:
        """
        Получить существующего пользователя или создать нового.
        
        Ищет пользователя по email.
        Если не найден - создаёт нового с переданными данными.
        
        Args:
            email: Email пользователя (уникальный)
            full_name: Полное имя пользователя
            
        Returns:
            tuple[User, bool]: Кортеж (пользователь, был_ли_создан)
                - User: найденный или созданный пользователь
                - bool: True если пользователь был создан, False если найден
        """
        # Пытаемся найти существующего пользователя
        user = await self.get_by_email(email)
        
        if user is not None:
            logger.debug(
                "Найден существующий пользователь",
                extra={
                    "user_id": user.id,
                    "email": email
                }
            )
            return user, False
        
        # Создаём нового пользователя
        user = await self.create(
            email=email,
            full_name=full_name
        )
        
        return user, True
    
    async def update(
        self,
        user_id: int,
        email: Optional[str] = None,
        full_name: Optional[str] = None
    ) -> Optional[User]:
        """
        Обновить данные пользователя.
        
        Args:
            user_id: ID пользователя
            email: Новый email (если передан)
            full_name: Новое имя (если передано)
            
        Returns:
            User | None: Обновлённый пользователь или None если не найден
        """
        user = await self.get_by_id(user_id)
        
        if user is None:
            logger.warning(
                "Попытка обновить несуществующего пользователя",
                extra={"user_id": user_id}
            )
            return None
        
        # Обновляем только переданные поля
        if email is not None:
            user.email = email
        if full_name is not None:
            user.full_name = full_name
        
        await self.session.commit()
        await self.session.refresh(user)
        
        logger.info(
            "Обновлены данные пользователя",
            extra={"user_id": user_id}
        )
        
        return user


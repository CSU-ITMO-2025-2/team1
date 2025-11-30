"""Зависимости для FastAPI endpoints."""
import json
from typing import Optional
import httpx
from fastapi import Depends, Form, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.rabbitmq import RabbitMQClient
from app.services.user_service import UserService
from app.services.generation_service import GenerationService
from app.services.logging_service import LoggingService
from app.api.schemas.common import UserData
from app.core.config import settings
from app.logger import setup_logger

logger = setup_logger(__name__)

# Глобальный клиент RabbitMQ (будет инициализирован в lifespan)
_rabbit_client: Optional[RabbitMQClient] = None


def set_rabbit_client(client: RabbitMQClient) -> None:
    """
    Установить глобальный RabbitMQ клиент.
    
    Args:
        client: Инициализированный клиент RabbitMQ
    """
    global _rabbit_client
    _rabbit_client = client


def get_rabbit_client() -> RabbitMQClient:
    """
    Получить RabbitMQ клиент.
    
    Returns:
        RabbitMQClient: Инициализированный клиент
        
    Raises:
        HTTPException: Если клиент не инициализирован
    """
    if _rabbit_client is None:
        raise HTTPException(
            status_code=500,
            detail="RabbitMQ клиент не инициализирован"
        )
    return _rabbit_client


async def get_db_session() -> AsyncSession:
    """
    Получить сессию БД.
    
    Yields:
        AsyncSession: Сессия SQLAlchemy
    """
    async for session in get_session():
        yield session


async def get_current_user(request: Request) -> Optional[dict]:
    """
    Получить текущего пользователя из auth_service.
    
    Проверяет cookie 'sid' через auth_service эндпоинт /me.
    
    Args:
        request: FastAPI Request объект
        
    Returns:
        Optional[dict]: Информация о пользователе или None
        
    Raises:
        HTTPException: Если авторизация обязательна и пользователь не авторизован
    """
    # Получаем cookie sid
    sid = request.cookies.get(settings.auth_cookie_name)
    
    if not sid:
        if settings.auth_required:
            logger.warning("Попытка доступа без cookie sid")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Требуется авторизация"
            )
        return None
    
    # Проверяем сессию через auth_service
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{settings.auth_service_url}/me",
                cookies={settings.auth_cookie_name: sid}
            )
            
            if response.status_code == 401:
                if settings.auth_required:
                    logger.warning("Недействительная или истекшая сессия")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Недействительная или истекшая сессия"
                    )
                return None
            
            response.raise_for_status()
            user_info = response.json()
            
            logger.info(
                "Успешная проверка авторизации",
                extra={"user": user_info.get("preferred_username", user_info.get("sub"))}
            )
            
            return user_info
            
    except httpx.HTTPError as e:
        logger.error(f"Ошибка при проверке авторизации через auth_service: {e}")
        if settings.auth_required:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Сервис авторизации недоступен"
            )
        return None


async def get_user_data(request: Request) -> Optional[UserData]:
    """
    Получить данные пользователя для создания/обновления в БД.
    
    Получает информацию из auth_service через cookie и преобразует в UserData.
    
    Args:
        request: FastAPI Request объект
        
    Returns:
        Optional[UserData]: Данные пользователя или None
    """
    user_info = await get_current_user(request)
    
    if not user_info:
        return None
    
    # Преобразуем данные из Keycloak в UserData
    email = user_info.get("email")
    full_name = user_info.get("name") or user_info.get("preferred_username") or email
    
    if email and full_name:
        return UserData(email=email, full_name=full_name)
    
    return None


async def require_auth(user_info: Optional[dict] = Depends(get_current_user)) -> dict:
    """
    Зависимость, требующая обязательной авторизации.
    
    Args:
        user_info: Информация о пользователе
        
    Returns:
        dict: Информация о пользователе
        
    Raises:
        HTTPException: Если пользователь не авторизован
    """
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется авторизация"
        )
    return user_info


def get_user_service(
    session: AsyncSession = Depends(get_db_session)
) -> UserService:
    """
    Получить сервис работы с пользователями.
    
    Args:
        session: Сессия БД
        
    Returns:
        UserService: Экземпляр сервиса
    """
    return UserService(session)


def get_generation_service(
    rabbit_client: RabbitMQClient = Depends(get_rabbit_client)
) -> GenerationService:
    """
    Получить сервис генерации.
    
    Args:
        rabbit_client: Клиент RabbitMQ
        
    Returns:
        GenerationService: Экземпляр сервиса
    """
    return GenerationService(rabbit_client)


def get_logging_service(
    session: AsyncSession = Depends(get_db_session)
) -> LoggingService:
    """
    Получить сервис логирования.
    
    Args:
        session: Сессия БД
        
    Returns:
        LoggingService: Экземпляр сервиса
    """
    return LoggingService(session)


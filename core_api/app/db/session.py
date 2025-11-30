"""
Управление сессиями SQLAlchemy для работы с PostgreSQL.

Модуль содержит:
- Настройку async движка SQLAlchemy
- Фабрику для создания async сессий
- Зависимость FastAPI для получения сессии БД
"""

from collections.abc import AsyncGenerator
from typing import Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
from app.logger import setup_logger

# Логгер для модуля
logger = setup_logger(__name__)

# Глобальные переменные для движка и фабрики сессий
_engine: Optional[AsyncEngine] = None
_async_session_maker: Optional[async_sessionmaker[AsyncSession]] = None


def init_db() -> None:
    """
    Инициализирует движок SQLAlchemy и фабрику сессий.
    
    Создаёт глобальный async движок и sessionmaker.
    Должна вызываться один раз при старте приложения.
    
    Raises:
        ValueError: Если параметры подключения некорректны
    """
    global _engine, _async_session_maker
    
    logger.info("Инициализация подключения к PostgreSQL")
    
    # Создаём async движок, используя URL из настроек
    _engine = create_async_engine(
        settings.postgres.url,
        echo=False,  # Логирование SQL запросов
        pool_pre_ping=True,  # Проверка соединения перед использованием
        pool_size=10,  # Размер пула соединений
        max_overflow=20,  # Максимальное количество дополнительных соединений
    )
    
    # Создаём фабрику для async сессий
    _async_session_maker = async_sessionmaker(
        _engine,
        class_=AsyncSession,
        expire_on_commit=True,  # Сбрасывать объекты после commit (предотвращает устаревшие данные)
        autoflush=True,  # Автоматический flush перед запросами (предсказуемое поведение)
        autocommit=False,  # Явный контроль транзакций
    )
    
    logger.info("Подключение к PostgreSQL успешно настроено")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Зависимость FastAPI для получения сессии БД.
    
    Создаёт новую async сессию для каждого запроса и
    автоматически закрывает её после завершения.
    
    Yields:
        AsyncSession: Сессия для работы с БД
        
    Raises:
        RuntimeError: Если БД не была инициализирована
    """
    if _async_session_maker is None:
        logger.error("База данных не инициализирована")
        raise RuntimeError(
            "База данных не инициализирована. "
        )
    
    # Создаём новую сессию
    async with _async_session_maker() as session:
        try:
            yield session
        except Exception as e:
            # В случае ошибки откатываем транзакцию
            await session.rollback()
            logger.error(
                "Ошибка при работе с БД, откат транзакции",
                extra={"тип_ошибки": type(e).__name__, "сообщение": str(e)}
            )
            raise
        finally:
            # Закрываем сессию
            await session.close()


async def close_db() -> None:
    """
    Закрывает все соединения с БД.
    
    Должна вызываться при остановке приложения
    для корректного освобождения ресурсов.
    """
    global _engine
    
    if _engine is not None:
        logger.info("Закрытие соединений с PostgreSQL")
        await _engine.dispose()
        _engine = None
        logger.info("Соединения с PostgreSQL закрыты")


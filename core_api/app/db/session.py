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

from app.db.config import get_database_url
from logger import setup_logger

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
    
    # Получаем URL подключения
    database_url = get_database_url(async_driver=True)
    
    logger.info("Инициализация подключения к PostgreSQL")
    
    # Создаём async движок
    _engine = create_async_engine(
        database_url,
        echo=False,  # Логирование SQL запросов (можно включить для отладки)
        pool_pre_ping=True,  # Проверка соединения перед использованием
        pool_size=10,  # Размер пула соединений
        max_overflow=20,  # Максимальное количество дополнительных соединений
    )
    
    # Создаём фабрику для async сессий
    _async_session_maker = async_sessionmaker(
        _engine,
        class_=AsyncSession,
        expire_on_commit=False,  # Не сбрасывать объекты после commit
        autoflush=False,  # Не выполнять автоматический flush
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
        
    Example:
        ```python
        @app.get("/users")
        async def get_users(session: AsyncSession = Depends(get_session)):
            result = await session.execute(select(User))
            return result.scalars().all()
        ```
    """
    if _async_session_maker is None:
        logger.error("База данных не инициализирована")
        raise RuntimeError(
            "База данных не инициализирована. "
            "Вызовите init_db() при старте приложения."
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


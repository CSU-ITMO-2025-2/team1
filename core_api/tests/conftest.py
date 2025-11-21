"""
Конфигурация pytest и общие фикстуры для тестов.
"""

import asyncio
import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from app.db.base import Base
from app.db.models import GenerationResult, User
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

# Устанавливаем переменные окружения для тестовой БД
os.environ["POSTGRES_HOST"] = "localhost"
os.environ["POSTGRES_PORT"] = "5432"
os.environ["POSTGRES_DB"] = "hr_assist_test"
os.environ["POSTGRES_USER"] = "postgres"
os.environ["POSTGRES_PASSWORD"] = os.getenv("POSTGRES_PASSWORD", "postgres")


# Тестовый URL для PostgreSQL
TEST_DATABASE_URL = (
    f"postgresql+asyncpg://{os.environ['POSTGRES_USER']}:"
    f"{os.environ['POSTGRES_PASSWORD']}@"
    f"{os.environ['POSTGRES_HOST']}:{os.environ['POSTGRES_PORT']}/"
    f"{os.environ['POSTGRES_DB']}"
)


@pytest.fixture(scope="session")
def event_loop():
    """
    Создаёт event loop для всех async тестов в сессии.

    Yields:
        asyncio.AbstractEventLoop: Event loop для тестов
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def engine():
    """
    Создаёт async engine для тестовой БД.

    Yields:
        AsyncEngine: SQLAlchemy async engine
    """
    test_engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,  # Отключаем пулинг для тестов
    )

    # Создаём таблицы
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield test_engine

    # Очищаем таблицы после теста
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def session(engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Создаёт async сессию для каждого теста.

    Args:
        engine: Async engine из фикстуры

    Yields:
        AsyncSession: Сессия для работы с БД в тесте
    """
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )

    async with async_session_maker() as test_session:
        yield test_session


@pytest_asyncio.fixture
async def sample_user(session: AsyncSession) -> User:
    """
    Создаёт тестового пользователя в БД.

    Args:
        session: Async сессия БД

    Returns:
        User: Созданный пользователь
    """
    user = User(
        auth_provider="test_provider",
        external_id="test_external_123",
        email="test@example.com",
        full_name="Тестовый Пользователь",
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user


@pytest_asyncio.fixture
async def sample_generation_result(
    session: AsyncSession, sample_user: User
) -> GenerationResult:
    """
    Создаёт тестовый результат генерации в БД.

    Args:
        session: Async сессия БД
        sample_user: Тестовый пользователь

    Returns:
        GenerationResult: Созданный результат генерации
    """
    result = GenerationResult(
        user_id=sample_user.id,
        request_type="resume_evaluation",
        request_payload={"test": "data"},
        response_payload={"result": "success"},
        model_name="test_model",
        status="success",
        tokens_input=100,
        tokens_output=200,
        latency_ms=1500,
    )

    session.add(result)
    await session.commit()
    await session.refresh(result)

    return result

"""
Конфигурация Alembic для миграций базы данных.

Поддерживает:
- Async SQLAlchemy с asyncpg
- Автоматическую генерацию миграций из ORM моделей
- Загрузку настроек из переменных окружения
"""

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Импортируем Base и модели для автогенерации
from app.db.base import Base
from app.db.config import get_database_url
# Импортируем модели чтобы они были зарегистрированы в MetaData
from app.db.models import User, GenerationResult  # noqa: F401

# Объект конфигурации Alembic
config = context.config

# Интерпретация конфигурационного файла для логирования
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Устанавливаем URL из переменных окружения
# Используем асинхронный драйвер (asyncpg), так как run_async_migrations использует async_engine_from_config
config.set_main_option("sqlalchemy.url", get_database_url(async_driver=True))

# MetaData для автогенерации миграций из моделей
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """
    Выполнение миграций в 'offline' режиме.

    Конфигурирует контекст только с URL без создания Engine.
    В этом режиме не требуется DBAPI.
    Вызовы context.execute() выводят SQL в скрипт.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # Сравнение типов при автогенерации
        compare_server_default=True,  # Сравнение дефолтных значений
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """
    Выполнение миграций с установленным соединением.
    
    Args:
        connection: Соединение с БД
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,  # Сравнение типов при автогенерации
        compare_server_default=True,  # Сравнение дефолтных значений
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Выполнение миграций в async режиме.
    
    Создаёт async engine и выполняет миграции
    в синхронном режиме через run_sync().
    """
    # Создаём async engine для миграций
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        # Выполняем миграции в синхронном контексте
        await connection.run_sync(do_run_migrations)

    # Закрываем engine
    await connectable.dispose()


def run_migrations_online() -> None:
    """
    Выполнение миграций в 'online' режиме.

    Создаёт Engine и ассоциирует соединение с контекстом.
    Использует asyncio для async SQLAlchemy.
    """
    asyncio.run(run_async_migrations())


# Определяем режим выполнения миграций
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

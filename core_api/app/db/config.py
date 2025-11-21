"""
Конфигурация подключения к базе данных PostgreSQL.

Использует глобальные настройки из app.core.config.
"""

from app.core.config import settings


def get_database_url(async_driver: bool = True) -> str:
    """
    Возвращает URL подключения к БД из настроек.
    
    Args:
        async_driver: Если True - возвращает URL для asyncpg, иначе для psycopg2.
        
    Returns:
        str: URL подключения.
    """
    if async_driver:
        return settings.postgres.url
    return settings.postgres.sync_url

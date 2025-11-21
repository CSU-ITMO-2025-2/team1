"""
Модуль для работы с базой данных PostgreSQL.

Содержит:
- Настройку подключения к PostgreSQL через SQLAlchemy async
- Базовый класс для ORM моделей
- Зависимость для получения сессии в FastAPI
"""

from app.db.base import Base
from app.db.session import get_session, init_db

__all__ = ["Base", "get_session", "init_db"]


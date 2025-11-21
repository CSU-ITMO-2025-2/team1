"""
Базовый класс для ORM моделей SQLAlchemy.

Модуль определяет DeclarativeBase, от которого наследуются
все модели данных приложения.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Базовый класс для всех ORM моделей.
    
    Используется SQLAlchemy 2.x DeclarativeBase для определения
    метаданных и конфигурации всех таблиц БД.
    """
    pass


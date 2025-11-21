"""
Репозитории для работы с данными.

Содержит классы для выполнения операций с БД через паттерн Repository.
"""

from app.repositories.user import UserRepository
from app.repositories.generation_result import GenerationResultRepository

__all__ = ["UserRepository", "GenerationResultRepository"]


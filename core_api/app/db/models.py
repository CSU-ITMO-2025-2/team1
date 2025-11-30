"""
ORM модели для таблиц PostgreSQL.

Модуль содержит модели для:
- users: авторизованные пользователи системы
- generation_results: результаты работы LLM/ML воркеров
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    """
    Модель пользователя системы.

    Хранит информацию только об авторизованных пользователях.
    Используется для связи результатов генераций с конкретным пользователем.

    Attributes:
        id: Уникальный идентификатор пользователя
        email: Email пользователя (уникальный)
        full_name: Полное имя пользователя
        created_at: Дата и время создания записи
        updated_at: Дата и время последнего обновления
        generation_results: Связь с результатами генераций пользователя
    """

    __tablename__ = "users"

    # Первичный ключ
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="Уникальный идентификатор пользователя",
    )

    # Персональные данные
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        comment="Email пользователя (уникальный)",
    )

    full_name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Полное имя пользователя"
    )

    # Временные метки
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Дата и время создания записи",
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Дата и время последнего обновления",
    )

    # Связи
    generation_results: Mapped[list["GenerationResult"]] = relationship(
        "GenerationResult", back_populates="user", lazy="selectin"
    )

    # Индексы определены ниже через __table_args__
    __table_args__ = (
        # Индекс по email для поиска
        Index("ix_users_email", "email", unique=True),
        {"comment": "Таблица авторизованных пользователей"},
    )

    def __repr__(self) -> str:
        """Строковое представление пользователя."""
        return (
            f"<User(id={self.id}, email='{self.email}', full_name='{self.full_name}')>"
        )


class GenerationResult(Base):
    """
    Модель результата генерации LLM/ML воркера.

    Логирует все запросы к воркерам генерации (описание вакансий,
    оценка резюме, генерация вопросов и т.п.) с сохранением
    входных/выходных данных и метрик.

    Attributes:
        id: Уникальный идентификатор записи
        user_id: ID пользователя (NULL для анонимных запросов)
        request_type: Тип генерации (job_description, resume_evaluation, etc.)
        request_payload: Входные данные запроса в формате JSON
        response_payload: Результат генерации в формате JSON
        status: Статус выполнения (success, error, timeout)
        error_message: Сообщение об ошибке (если есть)
        latency_ms: Время выполнения в миллисекундах
        created_at: Дата и время создания записи
        user: Связь с пользователем
    """

    __tablename__ = "generation_results"

    # Первичный ключ
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="Уникальный идентификатор записи",
    )

    # Связь с пользователем (опционально)
    user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID пользователя (NULL для анонимных запросов)",
    )

    # Тип запроса
    request_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Тип генерации (job_description, resume_evaluation, etc.)",
    )

    # Данные запроса и ответа
    request_payload: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True, comment="Входные данные запроса"
    )

    response_payload: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True, comment="Результат генерации"
    )

    # Статус выполнения
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="success",
        comment="Статус выполнения (success, error, timeout)",
    )

    error_message: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Сообщение об ошибке"
    )

    # Метрики
    latency_ms: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="Время выполнения в миллисекундах"
    )

    # Временная метка
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Дата и время создания записи",
    )

    # Связи
    user: Mapped[Optional["User"]] = relationship(
        "User", back_populates="generation_results", lazy="selectin"
    )

    # Индексы
    __table_args__ = (
        Index("ix_generation_results_user_id", "user_id"),
        Index("ix_generation_results_request_type", "request_type"),
        Index("ix_generation_results_created_at", "created_at"),
        Index("ix_generation_results_status", "status"),
        {"comment": "Таблица результатов генераций LLM/ML воркеров"},
    )

    def __repr__(self) -> str:
        """Строковое представление результата генерации."""
        return (
            f"<GenerationResult(id={self.id}, "
            f"user_id={self.user_id}, "
            f"request_type='{self.request_type}', "
            f"status='{self.status}')>"
        )

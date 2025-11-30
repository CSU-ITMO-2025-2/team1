"""Общие схемы данных."""
from typing import Optional
from pydantic import BaseModel, Field


class UserData(BaseModel):
    """Данные пользователя, передаваемые с фронтенда."""
    
    email: str = Field(
        ...,
        description="Email пользователя"
    )
    full_name: str = Field(
        ...,
        description="Полное имя пользователя"
    )


class HealthResponse(BaseModel):
    """Ответ health check."""
    
    status: str = Field(
        ...,
        description="Статус работоспособности сервиса"
    )
    rabbitmq_status: Optional[str] = Field(
        None,
        description="Статус подключения к RabbitMQ"
    )
    db_status: Optional[str] = Field(
        None,
        description="Статус подключения к PostgreSQL"
    )


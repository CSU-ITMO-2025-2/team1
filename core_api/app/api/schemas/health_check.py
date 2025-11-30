from pydantic import BaseModel, Field
from typing import Optional

class HealthResponse(BaseModel):
    """Ответ health check."""

    status: str = Field(..., description="Статус работоспособности сервиса")
    rabbitmq_status: Optional[str] = Field(
        None, description="Статус подключения к RabbitMQ"
    )
    db_status: Optional[str] = Field(
        None, description="Статус подключения к PostgreSQL"
    )

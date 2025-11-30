"""Конфигурация приложения Core API."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


class PostgresConfig(ConfigBase):
    """Настройки базы данных PostgreSQL."""

    model_config = SettingsConfigDict(env_prefix="postgres_")

    host: str
    port: int
    db: str
    user: str
    password: str

    @property
    def url(self) -> str:
        """URL для асинхронного подключения к postgres."""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


class RabbitMQConfig(ConfigBase):
    """Настройки RabbitMQ."""

    model_config = SettingsConfigDict(env_prefix="rabbitmq_")

    default_user: str
    default_pass: str
    default_host: str
    port: int
    default_vhost: str

    @property
    def url(self) -> str:
        """URL подключения к RabbitMQ."""
        return f"amqp://{self.default_user}:{self.default_pass}@{self.default_host}:{self.port}{self.default_vhost}"


class Settings(BaseSettings):
    """Главный класс настроек."""

    postgres: PostgresConfig = Field(default_factory=PostgresConfig)
    rabbitmq: RabbitMQConfig = Field(default_factory=RabbitMQConfig)

    # Общие настройки
    core_api_port: int = 8000
    
    # Auth настройки
    auth_service_url: str = Field(
        default="http://auth_service:9000",
        description="URL auth service для проверки авторизации"
    )
    auth_required: bool = Field(
        default=False,
        description="Требовать авторизацию для всех эндпоинтов"
    )
    auth_cookie_name: str = Field(
        default="sid",
        description="Имя cookie с session ID"
    )


settings = Settings()

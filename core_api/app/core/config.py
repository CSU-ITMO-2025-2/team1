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

    host: str = "localhost"
    port: int = 5432
    db: str = "hr_assist"
    user: str = "postgres"
    password: str  # Обязательное поле

    @property
    def url(self) -> str:
        """URL для асинхронного подключения (asyncpg)."""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"

    @property
    def sync_url(self) -> str:
        """URL для синхронного подключения (psycopg2) - для Alembic."""
        return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


class RabbitMQConfig(ConfigBase):
    """Настройки RabbitMQ."""

    model_config = SettingsConfigDict(env_prefix="rabbitmq_")

    default_user: str = "guest"
    default_pass: str = "guest"
    default_host: str = "localhost"
    port: int = 5672
    default_vhost: str = "/"

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


settings = Settings()

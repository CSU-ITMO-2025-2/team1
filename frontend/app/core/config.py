"""Конфиг приложения."""

from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


class StreamlitConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="streamlit_")

    server_address: str
    server_port: int
    server_headless: bool
    browser_gather_usage_stats: bool
    theme_base: str


class LoggingConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="log_")

    level: str


class Config(BaseSettings):
    streamlit: StreamlitConfig = Field(default_factory=StreamlitConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    @classmethod
    def load(x) -> "Config":
        return x()


def check_env() -> bool:
    """Печатает статус проверки env и возвращает True/False."""
    try:
        cfg = Config.load()
    except ValidationError as e:
        print("Конфиг не загружен. Проверьте переменные:")
        for err in e.errors():
            loc = ".".join(str(x) for x in err.get("loc", ()))
            msg = err.get("msg", "Ошибка валидации")
            if loc.startswith("streamlit."):
                field = loc.split(".", 1)[1]
                hint = f"STREAMLIT_{field.upper()} / streamlit_{field}"
            elif loc.startswith("logging."):
                field = loc.split(".", 1)[1]
                hint = f"LOG_{field.upper()} / log_{field}"
            else:
                hint = ""
            print(f" - {loc}: {msg}" + (f" (проверь {hint})" if hint else ""))
        return False

    # Доп.проверка допустимых значений уровня логирования
    allowed = {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"}
    lvl = (cfg.logging.level or "").upper()
    if lvl not in allowed:
        print(
            "❌ logging.level: недопустимое значение "
            f"'{cfg.logging.level}'. Ожидается: {', '.join(sorted(allowed))} "
            "(проверь LOG_LEVEL / log_level)",
        )
        return False

    print("✅ Конфиг OK")
    return True


if __name__ == "__main__":
    check_env()

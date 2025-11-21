"""Файл запуска приложения"""

import os
import sys
from pathlib import Path

from pydantic import ValidationError

from app.core.config import Config
from logger import get_logger


def run() -> None:
    log = get_logger(__name__)

    # Проверка окружения
    try:
        cfg = Config.load()
    except ValidationError as e:
        log.error("Конфигурация невалидна:\n%s", e)
        sys.exit(1)

    # Расположение
    app_file = (Path(__file__).resolve().parent / "app" / "streamlit_app.py").as_posix()
    if not os.path.exists(app_file):
        log.error("Не найден файл приложения: %s", app_file)
        sys.exit(2)

    # Аргументы Streamlit
    args = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        app_file,
        "--server.address",
        cfg.streamlit.server_address,
        "--server.port",
        str(cfg.streamlit.server_port),
        "--server.headless",
        f"{cfg.streamlit.server_headless}",
    ]

    log.info("Exec: %s", " ".join(args[2:]))
    os.execvpe(args[0], args, os.environ)


if __name__ == "__main__":
    run()

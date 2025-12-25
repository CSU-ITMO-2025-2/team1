FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org uv

COPY pyproject.toml uv.lock ./

# Создать виртуальное окружение и установить зависимости
RUN UV_HTTP_TIMEOUT=300 uv sync \
    --allow-insecure-host pypi.org \
    --allow-insecure-host files.pythonhosted.org \
    --allow-insecure-host github.com \
    --no-native-tls

ENV PYTHONPATH=/app

COPY . .

# Использовать Python из виртуального окружения напрямую
CMD [".venv/bin/python", "-m", "worker"]
FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org uv

COPY core_api/pyproject.toml core_api/uv.lock ./

RUN UV_HTTP_TIMEOUT=300 uv sync \
    --allow-insecure-host pypi.org \
    --allow-insecure-host files.pythonhosted.org \
    --allow-insecure-host github.com \
    --no-native-tls

COPY core_api/ .

# Исправляем окончания строк и даем права на выполнение entrypoint.sh
RUN sed -i 's/\r$//' entrypoint.sh && chmod +x entrypoint.sh

# Устанавливаем ENTRYPOINT
ENTRYPOINT ["./entrypoint.sh"]

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org uv

COPY job_description_service/pyproject.toml job_description_service/uv.lock ./

RUN UV_HTTP_TIMEOUT=300 uv sync \
    --allow-insecure-host pypi.org \
    --allow-insecure-host files.pythonhosted.org \
    --allow-insecure-host github.com \
    --no-native-tls

ENV PYTHONPATH=/app

COPY job_description_service/ ./job_description_service

CMD ["uv", "run", "python", "-m", "job_description_service.worker"]
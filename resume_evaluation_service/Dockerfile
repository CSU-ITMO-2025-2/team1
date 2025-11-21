FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org uv

COPY resume_evaluation_service/pyproject.toml resume_evaluation_service/uv.lock ./

RUN UV_HTTP_TIMEOUT=300 uv sync \
    --allow-insecure-host pypi.org \
    --allow-insecure-host files.pythonhosted.org \
    --allow-insecure-host github.com \
    --no-native-tls

ENV PYTHONPATH=/app

COPY resume_evaluation_service/ ./resume_evaluation_service

CMD ["uv", "run", "python", "-m", "resume_evaluation_service.worker"]
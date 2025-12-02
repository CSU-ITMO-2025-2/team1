FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org uv

COPY pyproject.toml uv.lock ./

RUN UV_HTTP_TIMEOUT=300 uv sync \
    --allow-insecure-host pypi.org \
    --allow-insecure-host files.pythonhosted.org \
    --allow-insecure-host github.com \
    --no-native-tls

COPY . .


CMD ["uv", "run", "main.py"]
"""
Core API - Основной сервис HR-ассистента.

Предоставляет эндпоинты для:
- Оценки резюме
- Генерации описаний вакансий
- Генерации вопросов для интервью
"""

from fastapi import FastAPI

from .api.routes import health, job_description, questions, resume
from .core.lifespan import lifespan
from .middleware.error_handler import ErrorHandlerMiddleware


app = FastAPI(
    title="Core API",
    description="API для HR-ассистента",
    version="1.0.0",
    lifespan=lifespan,
)

# Подключение middleware
app.add_middleware(ErrorHandlerMiddleware)

# Подключение роутов
app.include_router(health.router)
app.include_router(resume.router)
app.include_router(job_description.router)
app.include_router(questions.router)

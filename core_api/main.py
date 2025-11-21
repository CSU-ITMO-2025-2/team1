"""
Core API - Основной сервис HR-ассистента

Этот модуль реализует FastAPI сервис, который:
1. Обрабатывает входящие HTTP запросы для оценки резюме и генерации описаний вакансий
2. Взаимодействует с RabbitMQ для асинхронной обработки задач
3. Предоставляет эндпоинты:
   - /resume_evaluation: оценка соответствия резюме и вакансии
   - /generate_vacancy_description: генерация описания вакансии
   - /health: проверка работоспособности сервиса

Зависимости:
- FastAPI для HTTP сервера
- RabbitMQ для асинхронной обработки
- Кастомный логгер для унифицированного логирования
"""

import json
import time
from typing import Optional

# Импорты для работы с БД
from app.db import get_session, init_db
from app.db.session import close_db
from app.repositories import GenerationResultRepository, UserRepository
# Импорт настроек
from app.core.config import settings
from extract_files.extract_text_from_file import file_to_text
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from logger import setup_logger
from pydantic import BaseModel
from rabbitmq import RabbitMQClient
from sqlalchemy.ext.asyncio import AsyncSession


# Простая модель для данных пользователя с фронтенда
class UserData(BaseModel):
    """Данные пользователя, передаваемые с фронтенда."""

    auth_provider: str = "keycloak"
    external_id: str
    email: Optional[str] = None
    full_name: Optional[str] = None


app = FastAPI(title="Core API")

# Логирование
logger = setup_logger(__name__)

# Глобальный клиент RabbitMQ
rabbit_client: RabbitMQClient = None


async def get_rabbit_client() -> RabbitMQClient:
    """
    Получение глобального клиента RabbitMQ.

    Returns:
        RabbitMQClient: Инициализированный клиент RabbitMQ

    Raises:
        HTTPException: Если клиент RabbitMQ не был инициализирован
    """
    if rabbit_client is None:
        raise HTTPException(
            status_code=500, detail="RabbitMQ клиент не инициализирован"
        )
    return rabbit_client


@app.on_event("startup")
async def startup():
    """
    Обработчик события запуска приложения.

    Выполняет:
    1. Инициализацию подключения к PostgreSQL
    2. Инициализацию глобального клиента RabbitMQ
    3. Установку соединения с RabbitMQ
    """
    global rabbit_client
    logger.info("Запуск Core API")

    # Инициализация БД
    try:
        init_db()
        logger.info("База данных успешно инициализирована")
    except Exception as e:
        logger.error(
            "Ошибка при инициализации БД", extra={"error": str(e)}, exc_info=True
        )
        # Не останавливаем приложение, продолжаем работу без БД

    # Инициализация RabbitMQ
    logger.info("Инициализация клиента RabbitMQ")
    rabbit_client = RabbitMQClient(settings.rabbitmq.url)
    await rabbit_client.connect()


# Добавить обработчик shutdown
@app.on_event("shutdown")
async def shutdown():
    """
    Обработчик события завершения работы приложения.

    Выполняет корректное закрытие соединений:
    1. Закрытие соединения с PostgreSQL
    2. Закрытие соединения с RabbitMQ
    """
    logger.info("Завершение работы Core API")

    # Закрытие подключения к БД
    try:
        await close_db()
    except Exception as e:
        logger.error("Ошибка при закрытии БД", extra={"error": str(e)})

    # Закрытие RabbitMQ
    if rabbit_client:
        await rabbit_client.close()


@app.post("/resume_evaluation")
async def get_resume_evaluation(
    # Текстовые данные (опционально)
    vacancy_text: Optional[str] = Form(None),
    resume_text: Optional[str] = Form(None),
    # Файлы (опционально)
    vacancy_file: Optional[UploadFile] = File(None),
    resume_file: Optional[UploadFile] = File(None),
    # Данные пользователя (опционально) - JSON строка
    user_data: Optional[str] = Form(None),
    # Зависимости
    rabbit_client: RabbitMQClient = Depends(get_rabbit_client),
    session: AsyncSession = Depends(get_session),
):
    """
    Эндпоинт для оценки соответствия резюме вакансии.

    Принимает данные в виде:
    - Текста (vacancy_text, resume_text)
    - Файлов (vacancy_file, resume_file) - поддерживаются .txt, .docx, .pdf
    - Комбинации текста и файлов

    Args:
        vacancy_text: Текст вакансии (опционально)
        resume_text: Текст резюме (опционально)
        vacancy_file: Файл с вакансией .txt/.docx/.pdf (опционально)
        resume_file: Файл с резюме .txt/.docx/.pdf (опционально)
        rabbit_client: Клиент RabbitMQ
        session: Сессия БД
        current_user: Текущий пользователь (опционально)

    Returns:
        dict: Результат оценки соответствия
    """
    start_time = time.time()
    logger.info("Начало обработки оценки резюме")

    try:
        # Получаем текст вакансии
        final_vacancy_text = ""
        if vacancy_text:
            final_vacancy_text = vacancy_text
            vacancy_source = "текст"
        elif vacancy_file:
            final_vacancy_text = await file_to_text(vacancy_file)
            if not final_vacancy_text:
                raise HTTPException(
                    status_code=400, detail="Не удалось извлечь текст из файла вакансии"
                )
            vacancy_source = f"файл ({vacancy_file.filename})"
        else:
            raise HTTPException(
                status_code=400,
                detail="Необходимо предоставить текст вакансии или файл с вакансией (.txt/.docx/.pdf)",
            )

        # Получаем текст резюме
        final_resume_text = ""
        if resume_text:
            final_resume_text = resume_text
            resume_source = "текст"
        elif resume_file:
            final_resume_text = await file_to_text(resume_file)
            if not final_resume_text:
                raise HTTPException(
                    status_code=400, detail="Не удалось извлечь текст из файла резюме"
                )
            resume_source = f"файл ({resume_file.filename})"
        else:
            raise HTTPException(
                status_code=400,
                detail="Необходимо предоставить текст резюме или файл с резюме (.txt/.docx/.pdf)",
            )

        logger.info(
            "Данные успешно получены",
            extra={
                "длина_вакансии": len(final_vacancy_text),
                "длина_резюме": len(final_resume_text),
                "источник_вакансии": vacancy_source,
                "источник_резюме": resume_source,
            },
        )

        logger.debug(
            "Отправка данных в очередь RabbitMQ",
            extra={"очередь": "resume_evaluation_task"},
        )

        # Парсим данные пользователя из формы (если есть)
        current_user = None
        if user_data:
            try:
                user_dict = json.loads(user_data)
                current_user = UserData(**user_dict)
                logger.debug(
                    "Получены данные пользователя",
                    extra={"external_id": current_user.external_id},
                )
            except Exception as e:
                logger.warning(f"Не удалось распарсить user_data: {e}")

        # Получаем или создаём пользователя в БД
        user_id = None
        if current_user:
            try:
                user_repo = UserRepository(session)
                user, _ = await user_repo.get_or_create_by_provider_id(
                    auth_provider=current_user.auth_provider,
                    external_id=current_user.external_id,
                    email=current_user.email,
                    full_name=current_user.full_name,
                )
                user_id = user.id
            except Exception as e:
                logger.error(
                    "Ошибка при работе с пользователем в БД", extra={"error": str(e)}
                )

        # Отправляем в очередь для оценки резюме
        result = await rabbit_client.call(
            {"vacancy_text": final_vacancy_text, "resume_text": final_resume_text},
            queue_name="resume_evaluation_task",
        )

        # Сохраняем результат в БД
        latency_ms = int((time.time() - start_time) * 1000)
        try:
            gen_repo = GenerationResultRepository(session)
            await gen_repo.create(
                request_type="resume_evaluation",
                status="success",
                user_id=user_id,
                request_payload={
                    "vacancy_source": vacancy_source,
                    "resume_source": resume_source,
                    "vacancy_length": len(final_vacancy_text),
                    "resume_length": len(final_resume_text),
                },
                response_payload=result
                if isinstance(result, dict)
                else {"result": str(result)},
                latency_ms=latency_ms,
            )
        except Exception as e:
            logger.error(
                "Ошибка при сохранении результата в БД", extra={"error": str(e)}
            )

        logger.info(
            "Успешная обработка оценки резюме",
            extra={"размер_ответа": len(str(result)), "latency_ms": latency_ms},
        )
        return result

    except HTTPException:
        # Сохраняем ошибку в БД
        try:
            latency_ms = int((time.time() - start_time) * 1000)
            gen_repo = GenerationResultRepository(session)
            await gen_repo.create(
                request_type="resume_evaluation",
                status="error",
                user_id=user_id if current_user else None,
                error_message="HTTP Exception",
                latency_ms=latency_ms,
            )
        except:
            pass
        # Перебрасываем HTTPException как есть
        raise
    except Exception as e:
        # Сохраняем ошибку в БД
        try:
            latency_ms = int((time.time() - start_time) * 1000)
            gen_repo = GenerationResultRepository(session)
            await gen_repo.create(
                request_type="resume_evaluation",
                status="error",
                user_id=user_id if current_user else None,
                error_message=str(e),
                latency_ms=latency_ms,
            )
        except:
            pass

        logger.error(
            "Ошибка при обработке оценки резюме",
            extra={"тип_ошибки": type(e).__name__, "сообщение": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка при обработке запроса"
        )


@app.post("/generate_vacancy_description")
async def generate_vacancy_description(
    # Текстовые данные (опционально)
    input_data: Optional[str] = Form(None),
    # Файл (опционально)
    input_file: Optional[UploadFile] = File(None),
    # Данные пользователя (опционально) - JSON строка
    user_data: Optional[str] = Form(None),
    # Зависимости
    rabbit_client: RabbitMQClient = Depends(get_rabbit_client),
    session: AsyncSession = Depends(get_session),
):
    """
    Эндпоинт для генерации описания вакансии.

    Принимает данные в виде текста или файла (.txt/.docx/.pdf).

    Args:
        input_data: Исходные данные в текстовом виде (опционально)
        input_file: Файл с исходными данными .txt/.docx/.pdf (опционально)
        rabbit_client: Клиент RabbitMQ
        session: Сессия БД
        current_user: Текущий пользователь (опционально)

    Returns:
        dict: Сгенерированное описание вакансии
    """
    start_time = time.time()
    logger.info("Начало генерации описания вакансии")

    try:
        # Получаем входные данные
        final_input_data = ""
        if input_data:
            final_input_data = input_data
            input_source = "текст"
        elif input_file:
            final_input_data = await file_to_text(input_file)
            if not final_input_data:
                raise HTTPException(
                    status_code=400, detail="Не удалось извлечь текст из файла"
                )
            input_source = f"файл ({input_file.filename})"
        else:
            raise HTTPException(
                status_code=400,
                detail="Необходимо предоставить входные данные в текстовом виде или в файле (.txt/.docx/.pdf)",
            )

        logger.info(
            "Данные успешно получены",
            extra={
                "длина_входных_данных": len(final_input_data),
                "источник_данных": input_source,
            },
        )

        logger.debug(
            "Отправка данных в очередь RabbitMQ",
            extra={"очередь": "job_description_task"},
        )

        # Парсим данные пользователя из формы (если есть)
        current_user = None
        if user_data:
            try:
                user_dict = json.loads(user_data)
                current_user = UserData(**user_dict)
                logger.debug(
                    "Получены данные пользователя",
                    extra={"external_id": current_user.external_id},
                )
            except Exception as e:
                logger.warning(f"Не удалось распарсить user_data: {e}")

        # Получаем или создаём пользователя в БД
        user_id = None
        if current_user:
            try:
                user_repo = UserRepository(session)
                user, _ = await user_repo.get_or_create_by_provider_id(
                    auth_provider=current_user.auth_provider,
                    external_id=current_user.external_id,
                    email=current_user.email,
                    full_name=current_user.full_name,
                )
                user_id = user.id
            except Exception as e:
                logger.error(
                    "Ошибка при работе с пользователем в БД", extra={"error": str(e)}
                )

        # Отправляем в очередь для генерации описания вакансии
        result = await rabbit_client.call(
            {"input_data": final_input_data},
            queue_name="job_description_task",
        )

        # Сохраняем результат в БД
        latency_ms = int((time.time() - start_time) * 1000)
        try:
            gen_repo = GenerationResultRepository(session)
            await gen_repo.create(
                request_type="job_description",
                status="success",
                user_id=user_id,
                request_payload={
                    "input_source": input_source,
                    "input_length": len(final_input_data),
                },
                response_payload=result
                if isinstance(result, dict)
                else {"result": str(result)},
                latency_ms=latency_ms,
            )
        except Exception as e:
            logger.error(
                "Ошибка при сохранении результата в БД", extra={"error": str(e)}
            )

        logger.info(
            "Успешная генерация описания вакансии",
            extra={"размер_ответа": len(str(result)), "latency_ms": latency_ms},
        )
        return result

    except HTTPException:
        # Сохраняем ошибку в БД
        try:
            latency_ms = int((time.time() - start_time) * 1000)
            gen_repo = GenerationResultRepository(session)
            await gen_repo.create(
                request_type="job_description",
                status="error",
                user_id=user_id if current_user else None,
                error_message="HTTP Exception",
                latency_ms=latency_ms,
            )
        except:
            pass
        # Перебрасываем HTTPException как есть
        raise
    except Exception as e:
        # Сохраняем ошибку в БД
        try:
            latency_ms = int((time.time() - start_time) * 1000)
            gen_repo = GenerationResultRepository(session)
            await gen_repo.create(
                request_type="job_description",
                status="error",
                user_id=user_id if current_user else None,
                error_message=str(e),
                latency_ms=latency_ms,
            )
        except:
            pass

        logger.error(
            "Ошибка при генерации описания вакансии",
            extra={"тип_ошибки": type(e).__name__, "сообщение": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка при обработке запроса"
        )


@app.post("/question_generation")
async def question_generation(
    # Текстовые данные (опционально)
    vacancy_text: Optional[str] = Form(None),
    resume_text: Optional[str] = Form(None),
    # Файлы (опционально)
    vacancy_file: Optional[UploadFile] = File(None),
    resume_file: Optional[UploadFile] = File(None),
    # Данные пользователя (опционально) - JSON строка
    user_data: Optional[str] = Form(None),
    # Зависимости
    rabbit_client: RabbitMQClient = Depends(get_rabbit_client),
    session: AsyncSession = Depends(get_session),
):
    """
    Генерация вопросов для интервью на основе вакансии и резюме.

    Шаги:
    1) Получаем тексты вакансии и резюме (из текста или файла).
    2) Вызываем пайплайн оценки соответствия (resume_evaluation_task) и получаем report.
    3) Передаём report + исходные тексты в очередь question_generation_task.

    Args:
        vacancy_text: Текст вакансии (опционально)
        resume_text: Текст резюме (опционально)
        vacancy_file: Файл с вакансией (опционально)
        resume_file: Файл с резюме (опционально)
        rabbit_client: Клиент RabbitMQ
        session: Сессия БД
        current_user: Текущий пользователь (опционально)
    """
    start_time = time.time()
    logger.info("Начало генерации вопросов по вакансии и резюме")

    try:
        # --- 1) Получаем текст вакансии ---
        final_vacancy_text = ""
        if vacancy_text:
            final_vacancy_text = vacancy_text
            vacancy_source = "текст"
        elif vacancy_file:
            final_vacancy_text = await file_to_text(vacancy_file)
            if not final_vacancy_text:
                raise HTTPException(
                    status_code=400, detail="Не удалось извлечь текст из файла вакансии"
                )
            vacancy_source = f"файл ({vacancy_file.filename})"
        else:
            raise HTTPException(
                status_code=400,
                detail="Необходимо предоставить текст вакансии или файл с вакансией (.txt/.docx/.pdf)",
            )

        # --- 2) Получаем текст резюме ---
        final_resume_text = ""
        if resume_text:
            final_resume_text = resume_text
            resume_source = "текст"
        elif resume_file:
            final_resume_text = await file_to_text(resume_file)
            if not final_resume_text:
                raise HTTPException(
                    status_code=400, detail="Не удалось извлечь текст из файла резюме"
                )
            resume_source = f"файл ({resume_file.filename})"
        else:
            raise HTTPException(
                status_code=400,
                detail="Необходимо предоставить текст резюме или файл с резюме (.txt/.docx/.pdf)",
            )

        logger.info(
            "Данные успешно получены",
            extra={
                "длина_вакансии": len(final_vacancy_text),
                "длина_резюме": len(final_resume_text),
                "источник_вакансии": vacancy_source,
                "источник_резюме": resume_source,
            },
        )

        # --- 3) Шаг оценки соответствия (эквивалент вызову /resume_evaluation) ---
        logger.debug(
            "Отправка данных в очередь оценки резюме",
            extra={"очередь": "resume_evaluation_task"},
        )
        evaluation_report = await rabbit_client.call(
            {"vacancy_text": final_vacancy_text, "resume_text": final_resume_text},
            queue_name="resume_evaluation_task",
        )

        # Парсим данные пользователя из формы (если есть)
        current_user = None
        if user_data:
            try:
                user_dict = json.loads(user_data)
                current_user = UserData(**user_dict)
                logger.debug(
                    "Получены данные пользователя",
                    extra={"external_id": current_user.external_id},
                )
            except Exception as e:
                logger.warning(f"Не удалось распарсить user_data: {e}")

        # Получаем или создаём пользователя в БД
        user_id = None
        if current_user:
            try:
                user_repo = UserRepository(session)
                user, _ = await user_repo.get_or_create_by_provider_id(
                    auth_provider=current_user.auth_provider,
                    external_id=current_user.external_id,
                    email=current_user.email,
                    full_name=current_user.full_name,
                )
                user_id = user.id
            except Exception as e:
                logger.error(
                    "Ошибка при работе с пользователем в БД", extra={"error": str(e)}
                )

        # --- 4) Генерация вопросов на основе report + исходных текстов ---
        logger.debug(
            "Отправка данных в очередь генерации вопросов",
            extra={"очередь": "question_generation_task"},
        )
        payload = {
            "vacancy_text": final_vacancy_text,
            "resume_text": final_resume_text,
            "report": evaluation_report,  # результат предыдущего шага
        }
        result = await rabbit_client.call(
            payload,
            queue_name="question_generation_task",
        )

        # Сохраняем результат в БД
        latency_ms = int((time.time() - start_time) * 1000)
        try:
            gen_repo = GenerationResultRepository(session)
            await gen_repo.create(
                request_type="question_generation",
                status="success",
                user_id=user_id,
                request_payload={
                    "vacancy_source": vacancy_source,
                    "resume_source": resume_source,
                    "vacancy_length": len(final_vacancy_text),
                    "resume_length": len(final_resume_text),
                },
                response_payload=result
                if isinstance(result, dict)
                else {"result": str(result)},
                latency_ms=latency_ms,
            )
        except Exception as e:
            logger.error(
                "Ошибка при сохранении результата в БД", extra={"error": str(e)}
            )

        logger.info(
            "Успешная генерация вопросов",
            extra={"размер_ответа": len(str(result)), "latency_ms": latency_ms},
        )
        return result

    except HTTPException:
        # Сохраняем ошибку в БД
        try:
            latency_ms = int((time.time() - start_time) * 1000)
            gen_repo = GenerationResultRepository(session)
            await gen_repo.create(
                request_type="question_generation",
                status="error",
                user_id=user_id if current_user else None,
                error_message="HTTP Exception",
                latency_ms=latency_ms,
            )
        except:
            pass
        raise
    except Exception as e:
        # Сохраняем ошибку в БД
        try:
            latency_ms = int((time.time() - start_time) * 1000)
            gen_repo = GenerationResultRepository(session)
            await gen_repo.create(
                request_type="question_generation",
                status="error",
                user_id=user_id if current_user else None,
                error_message=str(e),
                latency_ms=latency_ms,
            )
        except:
            pass

        logger.error(
            "Ошибка при генерации вопросов",
            extra={"тип_ошибки": type(e).__name__, "сообщение": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка при обработке запроса"
        )


@app.get("/health")
def health():
    """
    Эндпоинт проверки работоспособности сервиса.

    Проверяет:
    1. Доступность сервиса
    2. Статус подключения к RabbitMQ

    Returns:
        dict: Статус работоспособности сервиса и его компонентов
    """
    # Проверяем подключение к RabbitMQ
    if (
        rabbit_client
        and rabbit_client.connection
        and not rabbit_client.connection.is_closed
    ):
        rabbit_status = "подключен"
    else:
        rabbit_status = "отключен"

    logger.info(
        "Проверка работоспособности сервиса",
        extra={
            "rabbitmq_статус": rabbit_status,
            "время_проверки": time.strftime("%Y-%m-%d %H:%M:%S"),
        },
    )
    return {"status": "healthy"}

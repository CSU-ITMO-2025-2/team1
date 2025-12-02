"""
Функция-обертка, которая обрабатывает входной текст и запускает процесс парсинга курсов из резюме.
"""

from typing import Optional

from utils.clean_text import clean_text
from utils.logger import setup_logger
from pipelines.education_evaluation.extract_courses_llm.extract_courses import (
    extract_course_llm,
)
from pipelines.education_evaluation.pydantic_models.extract_courses import (
    CourseList,
)

# Логирование
logger = setup_logger(__name__)


async def get_courses(text: str) -> Optional[CourseList]:
    """
    Асинхронно извлекает данные о курсах.

    Args:
        text (str): Текст вакансии или резюме.

    Returns:
        Извлечённые данные или None при ошибке.
    """
    if not text or not text.strip():
        logger.warning("Пустой текст для извлечения курсов")
        return {"status": "failed"}
        
    # очищаем текст
    logger.info("Очищаем текст от лишних символов ")
    cleaned_text = clean_text(text)

    try:
        result = await extract_course_llm(cleaned_text)
        
        # Проверяем, что результат не None
        if result is None:
            logger.error("Результат равен None")
            return {'status': 'failed'}

        # Переводим в словарь
        result_dict = result.model_dump()

        # Устанавливаем флаг успешного выполнения
        result_dict['status'] = 'success'
        return result_dict
        
    except Exception as e:
        logger.error("Ошибка выполнения", str(e), exc_info=True)
        return {"status": "failed"}

"""
Функция-обертка, которая обрабатывает входной текст и запускает процесс оценки релевантности курсов кандидата для указанной вакансии.
"""

from typing import Dict, List, Optional

from utils.clean_text import clean_text
from utils.logger import setup_logger

from pipelines.education_evaluation.relevance_course_llm.relevance_course import evaluate_courses_relevance_llm

# Логирование
logger = setup_logger(__name__)


async def get_courses_relevance(
    courses: List[Dict[str, str]], vacancy_text: str
) -> Optional[dict]:
    """
    Асинхронно оценивает релевантность курсов кандидата для указанной вакансии.

    Args:
        courses: Список курсов в формате:
                 [{"course_name": "...", "description": "..."}, ...]
        vacancy_text: Текст вакансии (требования, обязанности, описание должности).

    Returns:
        dict | None: Результат с полем 'courses', содержащим оценку релевантности,
                     или None при ошибке.
    """
    # Проверка на пустой список курсов
    if not courses:
        logger.warning("Список курсов пуст — релевантность не может быть оценена")
        return {"status": "failed"}

    # Проверка на пустой текст вакансии
    if not vacancy_text or not vacancy_text.strip():
        logger.warning(
            "Пустой текст вакансии — невозможно оценить релевантность курсов"
        )
        return {"status": "failed"}

    # Очищаем текст вакансии
    logger.info("Очищаем текст вакансии от лишних символов")
    cleaned_vacancy = clean_text(vacancy_text)

    # Очищаем описания и названия курсов
    cleaned_courses = []
    for course in courses:
        name = course.get("course_name", "").strip()
        desc = course.get("description", "").strip()
        cleaned_desc = clean_text(desc) if desc else ""
        cleaned_courses.append({"course_name": name, "description": cleaned_desc})

    try:
        logger.info("Оцениваем релевантность %d курсов", len(cleaned_courses))
        result = await evaluate_courses_relevance_llm(
            courses=cleaned_courses, vacancy=cleaned_vacancy
        )

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
        logger.error(
            f"Ошибка при оценке релевантности курсов: {str(e)}", exc_info=True
        )
        return {'status': 'failed'}

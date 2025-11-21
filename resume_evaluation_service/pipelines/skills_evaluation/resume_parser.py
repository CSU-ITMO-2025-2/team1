"""
Функция-обертка, которая обрабатывает входной текст и запускает процесс парсинга cкиллов из резюме.
"""

from typing import Optional

from ...utils.logger import setup_logger
from .pydantic_models.resume_parser import ParsedResumeSkills
from .resume_parser_llm.resume_parser import resume_parser_llm
from ...utils.clean_text import clean_text

# Логирование
logger = setup_logger(__name__)


async def get_resume_skills(resume: str) -> Optional[ParsedResumeSkills]:
    """
    Асинхронно извлекает навыки из резюме.

    Args:
        resume (str): Резюме в виде текста.

    Returns:
        Извлечённые данные или None при ошибке.
    """
    # Проверяем, что текст не пустой и не состоит только из пробелов
    if not resume or not resume.strip():
        logger.warning("Пустой текст для извлечения опыта работы")
        return {'status': 'failed'}

    # очищаем текст
    logger.info("Очищаем текст от лишних символов")
    cleaned_resume = clean_text(resume)
    try:
        result = await resume_parser_llm(cleaned_resume)

        # Проверяем, что результат не None
        if result is None:
            logger.error("Результат равен None")
            return {'status': 'failed'}

        # Переводим в словарь
        result_dict = result.model_dump()

        # Устанавливаем флаг успешного выполнения
        result_dict['status'] = 'success'
        logger.info("Извлечение навыков прошло успешно")
        return result_dict

    except Exception as e:
        logger.error(f"Ошибка выполнения: {str(e)}", exc_info=True)
        return {'status': 'failed'}

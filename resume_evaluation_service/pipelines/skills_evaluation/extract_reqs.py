"""
Функция-обертка, которая обрабатывает входной текст и запускает процесс парсинга требований вакансии.
"""

from typing import Optional

from pipelines.skills_evaluation.extract_reqs_llm.extract_reqs import extract_reqs_llm
from pipelines.skills_evaluation.pydantic_models.extract_reqs import ParsedJobRequirements
from utils.clean_text import clean_text
from utils.logger import setup_logger

# Логирование
logger = setup_logger(__name__)


async def get_reqs(vacancy: str) -> Optional[ParsedJobRequirements]:
    """
    Асинхронно извлекает требования вакансии

    Args:
        vacancy (str): Текст вакансии или резюме.

    Returns:
        Извлечённые данные или 'status': 'failed' при ошибке.
    """
    # Проверяем, что текст не пустой и не состоит только из пробелов
    if not vacancy or not vacancy.strip():
        logger.warning("Пустой текст для извлечения требований вакансии")
        return {'status': 'failed'}

    # очищаем текст
    logger.info("Очищаем текст от лишних символов")
    cleaned_vacancy = clean_text(vacancy)

    try:
        result = await extract_reqs_llm(cleaned_vacancy)

        # Проверяем, что результат не None
        if result is None:
            logger.error("Результат равен None")
            return {'status': 'failed'}

        # Переводим в словарь
        result_dict = result.model_dump()

        # Устанавливаем флаг успешного выполнения
        result_dict['status'] = 'success'
        logger.info("Извлечение требований прошло успешно")
        return result_dict
    except Exception as e:
        logger.error(f"Ошибка выполнения: {str(e)}", exc_info=True)
        return {'status': 'failed'}

"""
Функция-обертка, которая обрабатывает входной текст и запускает процесс парсинга требований к опыту работы.
"""

from typing import Optional

from ...utils.clean_text import clean_text
from ...utils.logger import setup_logger
from .extract_work_reqs_llm.extract_work_reqs import extract_work_reqs_llm
from .pydantic_models.extract_work_reqs import WorkExpInfo

# Логирование
logger = setup_logger(__name__)


async def get_work_reqs(vacancy: str) -> Optional[WorkExpInfo]:
    """
    Асинхронно извлекает данные об опыте работы.

    Args:
        vacancy (str): Текст вакансии или резюме.

    Returns:
        Извлечённые данные или None при ошибке.
    """
    
    # Проверка на пустой текст
    if not vacancy or not vacancy.strip():
        logger.warning("Пустой текст для извлечения опыта работы")
        return {'status': 'failed'}

    # очищаем текст
    logger.info("Очищаем текст от лишних символов")
    cleaned_vacancy = clean_text(vacancy)

    try:
        result = await extract_work_reqs_llm(cleaned_vacancy)
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
        logger.error(f"Ошибка выполнения: {str(e)}", exc_info=True)
        return {'status': 'failed'}

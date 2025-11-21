"""
Функция-обертка, которая обрабатывает входной текст и запускает процесс сравнения дополнительной информации.
"""

from typing import Optional

from ...utils.clean_text import clean_text
from ...utils.logger import setup_logger
from .additional_match_llm.additional_llm import additional_llm
from .pydantic_models.additional_info import WorkScheduleComparison

# Логирование
logger = setup_logger(__name__)

async def get_additional_info(
    resume: str, vacancy: str
) -> Optional[WorkScheduleComparison]:
    """
    Асинхронно извлекает и анализирует данные о дополнительной информации из текста.

    Args:
        resume (str): Текст резюме
        vacancy (str): Текст вакансии

    Returns:
        Извлечённые данные или None при ошибке.
    """
    # Проверяем на наличие вакансии и резюме
    if not resume or not resume.strip() or not vacancy or not vacancy.strip():
        logger.warning("Пустой текст для условий работы")
        return {'status': 'failed'}

    # очищаем текст
    logger.info("Очищаем текст от лишних символов")

    cleaned_resume = clean_text(resume)
    cleaned_vacancy = clean_text(vacancy)

    try:
        result = await additional_llm(resume=cleaned_resume, vacancy=cleaned_vacancy)
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

"""
Функция-обертка, которая обрабатывает входной текст и запускает процесс парсинга данных об опыте работы.
"""

from typing import Optional

from pipelines.work_exp_evaluation.extract_work_exp_llm.extract_work_exp import extract_work_exp_llm
from pipelines.work_exp_evaluation.pydantic_models.extract_work_exp import WorkExpList
from utils.clean_text import clean_text
from utils.logger import setup_logger

# Логирование
logger = setup_logger(__name__)


async def get_work_exp(resume: str) -> Optional[WorkExpList]:
    """
    Асинхронно извлекает данные об опыте работы.

    Args:
        resume (str): Текст резюме.

    Returns:
        Извлечённые данные или None при ошибке.
    """
    
    # Проверяем на пустой текст
    if not resume or not resume.strip():
        logger.warning("Пустой текст для извлечения опыта работы")
        return {"status": "failed"}

    # очищаем текст
    logger.info("Очищаем текст от лишних символов")
    cleaned_resume = clean_text(resume)

    try:
        result = await extract_work_exp_llm(cleaned_resume)
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
        return {"status": "failed"}

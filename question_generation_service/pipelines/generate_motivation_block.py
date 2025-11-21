"""
Функция-обертка, которая обрабатывает входной текст и запускает процесс генерации блока вопросов по мотивации.
"""

import asyncio
from typing import Optional

from ..utils.clean_text import clean_text
from ..utils.logger import setup_logger
from .motivation_block_llm.motivation_block import motivation_block_llm

# Логирование
logger = setup_logger(__name__)


async def get_motivation_block(vacancy: str, resume: str, work_experience_evaluation: str, salary_evaluation: str) -> dict:
    """
    Асинхронно генерирует блок вопросов по мотивации из входного текста.

    Args:
        vacancy (str): Текст вакансии.
        resume (str): Текст резюме.
        work_experience_evaluation (str): Оценка опыта работы.
        salary_evaluation (str): Оценка зарплаты.

    Returns:
        Извлечённые данные или None при ошибке.
    """
    # Проверяем, что входной текст присутствует и не пустой
    if not vacancy or not vacancy.strip():
        logger.warning("Пустой текст для парсинга вакансии")
        return {'status': 'failed'}
        
    # Проверяем, что входной текст присутствует и не пустой
    if not resume or not resume.strip():
        logger.warning("Пустой текст для парсинга вакансии")
        return {'status': 'failed'}
        
    # Проверяем, что входной текст присутствует и не пустой
    if not work_experience_evaluation or not work_experience_evaluation.strip():
        logger.warning("Пустой текст для парсинга вакансии")
        return {'status': 'failed'}
        
    # Проверяем, что входной текст присутствует и не пустой
    if not salary_evaluation or not salary_evaluation.strip():
        logger.warning("Пустой текст для парсинга вакансии")
        return {'status': 'failed'}

    # очищаем текст
    logger.info("Очищаем текст от лишних символов")
    cleaned_vacancy = clean_text(vacancy)
    cleaned_resume = clean_text(resume)
    cleaned_work_experience_evaluation = clean_text(work_experience_evaluation)
    cleaned_salary_evaluation = clean_text(salary_evaluation)

    try:
        # Вызываем функцию для парсинга вакансии
        result = await motivation_block_llm(cleaned_vacancy, cleaned_resume, cleaned_work_experience_evaluation, cleaned_salary_evaluation)
        
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



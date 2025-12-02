"""
Функция-обертка, которая обрабатывает входной текст и запускает процесс парсинга зарплаты.
"""

from typing import Optional

from utils.clean_text import clean_text
from utils.logger import setup_logger
from pipelines.salary_evaluation.pydantic_models.salary_extraction_model import SalaryData
from pipelines.salary_evaluation.salary_extraction.salary_extraction import extract_salary_llm

# Логирование
logger = setup_logger(__name__)


async def get_salary(text: str, text_type: str) -> Optional[SalaryData]:
    """
    Асинхронно извлекает данные о зарплате из текста.

    Args:
        text (str): Текст вакансии или резюме.
        text_type (str): Тип текста — "вакансии" или "резюме" (склонение для логов).

    Returns:
        Извлечённые данные или None при ошибке.
    """
    # Проверяем, что входной текст присутствует и не пустой
    if not text or not text.strip():
        logger.warning(f"Пустой текст для извлечения зарплаты (тип: {text_type})")
        return {'status': 'failed'}

    # Проверяем, что тип текста корректный
    if text_type not in ["вакансии", "резюме"]:
        logger.warning(f"Неверный тип текста для извлечения зарплаты (тип: {text_type})")
        return {'status': 'failed'}

    # очищаем текст
    logger.info(f"Очищаем текст от лишних символов для {text_type}")
    cleaned_text = clean_text(text)

    try:
        result = await extract_salary_llm(cleaned_text, text_type=text_type)

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
        logger.error(f"Ошибка выполнения для {text_type}: %s", str(e), exc_info=True)
        return {'status': 'failed'}

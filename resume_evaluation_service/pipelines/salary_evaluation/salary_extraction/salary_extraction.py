"""
Функция для создания запроса для парсинга зарплаты с структурированным выводом
с постепенным изменением температуры
"""

from typing import Optional

from ....pipelines.salary_evaluation.prompts.extract_sales import (
    salary_extraction_full_prompt,
)
from ....pipelines.salary_evaluation.pydantic_models.salary_extraction_model import (
    SalaryData,
)
from ....utils.create_llm_with_retries import get_structured_llm
from ....utils.logger import setup_logger

# Логирование
logger = setup_logger(__name__)

# Максимальное количество попыток
MAX_ATTEMPTS = 10

async def extract_salary_llm(text: str, text_type: str) -> Optional[SalaryData]:
    """
    Создаёт экземпляр LLM, настроенный на структурированный вывод указанной Pydantic-модели.
    Температура модели плавно увеличивается с номером попытки, что повышает вероятность
    корректного парсинга при повторных вызовах в случае ошибок (например, из-за "грязных" символов).

    Args:
        text (str): Текст описания вакансии
        text_type (str): Тип текста (например, "вакансии", "резюме") - склонение для логов

    Returns:
        ChatOpenAI: Экземпляр LLM, привязанный к схеме вывода через `.with_structured_output()`.
    """

    # Последняя ошибка
    last_exception = None

    # Для каждой попытки
    for attempt in range(1, MAX_ATTEMPTS + 1):
        logger.info(f"Попытка {attempt}/{MAX_ATTEMPTS} для {text_type}")

        try:
            # Получаем LLM с нужной температурой для этой попытки
            structured_llm = get_structured_llm(
                pydantic_model=SalaryData, attempt_number=attempt
            )

            # Формируем промпт
            prompt_input = {"text": text, "text_type": text_type}
            messages = await salary_extraction_full_prompt.ainvoke(prompt_input)

            # Выполняем запрос
            response = await structured_llm.ainvoke(messages)
            logger.info(
                f"Успешно получено значение после {attempt} попытки для {text_type}"
            )
            return response

        except Exception as e:
            last_exception = e
            logger.warning(
                f"Ошибка при попытке {attempt}: {str(e)} для {text_type}"
            )

            if attempt == MAX_ATTEMPTS:
                break

    # Все попытки провалились
    logger.error(
        f"Все попыток извлечь зарплату из {text_type} провалились: {str(last_exception)}",
        exc_info=True,
    )
    return None

"""
Функция для создания запроса для извлечения опыта работы с структурированным выводом
с постепенным изменением температуры
"""

from typing import Optional

from ..prompts.extract_work_exp.prompt_builder import work_experience_full_prompt
from ..pydantic_models.extract_work_exp import WorkExpList
from ....utils.create_llm_with_retries import get_structured_llm
from ....utils.logger import setup_logger

# Логирование
logger = setup_logger(__name__)

# Максимальное количество попыток
MAX_ATTEMPTS = 10


async def extract_work_exp_llm(resume: str) -> Optional[WorkExpList]:
    """
    Создаёт экземпляр LLM, настроенный на структурированный вывод опыта работы.
    Температура модели плавно увеличивается с номером попытки, что повышает вероятность
    корректного парсинга при повторных вызовах в случае ошибок (например, из-за "грязных" символов).

    Args:
        resume (str): Текст резюме для извлечения опыта работы.
    
    Returns:
        ChatOpenAI: Экземпляр LLM, привязанный к схеме вывода через `.with_structured_output()`.
    """
    # Последняя ошибка
    last_exception = None

    # Для каждой попытки
    for attempt in range(1, MAX_ATTEMPTS + 1):
        logger.info(f"Попытка {attempt}/{MAX_ATTEMPTS}")

        try:
            # Получаем LLM с нужной температурой для этой попытки
            structured_llm = get_structured_llm(
                pydantic_model=WorkExpList, attempt_number=attempt
            )

            # Формируем промпт
            prompt_input = {"resume": resume}
            messages = await work_experience_full_prompt.ainvoke(prompt_input)

            # Выполняем запрос
            response = await structured_llm.ainvoke(messages)
            logger.info(f"Успешно получено значение после {attempt} попытки")
            return response

        except Exception as e:
            last_exception = e
            logger.warning(f"Ошибка при попытке {attempt}: {str(e)}")

            if attempt == MAX_ATTEMPTS:
                break

    # Все попытки провалились
    logger.error(
        f"Все {MAX_ATTEMPTS} попыток извлечь опыт работы провалились: {str(last_exception)}",
        exc_info=True,
    )
    return None

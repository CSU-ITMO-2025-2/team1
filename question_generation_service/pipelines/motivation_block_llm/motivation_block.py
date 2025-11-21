"""
Функция для создания запроса для генерации вопросов блока мотивации с структурированным выводом 
с постепенным изменением температуры
"""

import asyncio
from typing import Optional

from ...utils.create_llm_with_retries import get_structured_llm
from ...utils.logger import setup_logger
from ..prompts.motivation_block.prompt_builder import motivaion_block_full_prompt
from ..pydantic_models.questions_blocks import MotivationBlock

# Логирование
logger = setup_logger(__name__)

# Максимальное количество попыток
MAX_ATTEMPTS = 10


async def motivation_block_llm(vacancy: str, resume: str, work_experience_evaluation: str, salary_evaluation: str) -> Optional[MotivationBlock]:
    """
    Создаёт экземпляр LLM, настроенный на структурированный вывод блока мотивации.
    Температура в запросе плавно увеличивается с номером попытки, что повышает вероятность
    корректного парсинга при повторных вызовах в случае ошибок (например, из-за "грязных" символов).

    Args:
        vacancy (str): Текст вакансии.
        resume (str): Текст резюме.
        work_experience_evaluation (str): Оценка работы.
        salary_evaluation (str): Оценка зарплаты.

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
                pydantic_model=MotivationBlock, attempt_number=attempt
            )

            # Формируем промпт
            prompt_input = {"vacancy_text": vacancy, 
                            "resume_text": resume,
                            "work_experience_evaluation": work_experience_evaluation,
                            "salary_evaluation": salary_evaluation}
            messages = await motivaion_block_full_prompt.ainvoke(prompt_input)

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
        f"Все {MAX_ATTEMPTS} попыток cгенерировать блок вопросов провалились: {str(last_exception)}",
        exc_info=True,
    )
    return None

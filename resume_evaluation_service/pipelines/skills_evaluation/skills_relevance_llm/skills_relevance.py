"""
Модуль для оценки релевантности курсов кандидата относительно вакансии.
Использует LLM с динамической Pydantic-моделью для структурированного вывода.
"""

from typing import Optional

from langchain_core.messages import BaseMessage
from pydantic import BaseModel

from utils.create_llm_with_retries import get_structured_llm
from utils.logger import setup_logger
from pipelines.skills_evaluation.prompts.skills_relevance.prompt_builder import skills_relevance_full_prompt
from pipelines.skills_evaluation.pydantic_models.skills_relevance import (
    create_pydantic_skills_relevance_matching_model,
)

# Логирование
logger = setup_logger(__name__)

# Максимальное количество попыток
MAX_ATTEMPTS = 10


async def skills_relevance_llm(
    unmatched_vac_list: list, unmatched_res_list: list, pairs
) -> Optional[BaseModel]:
    """
    Асинхронно оценивает релевантность скилов.

    Args:
        unmatched_vac_list: Список несовпадающих вакансий.
        unmatched_res_list: Список несовпадающих резюме.
        pairs: Список пар (вакансия, резюме).

    Returns:
        Экземпляр Pydantic-модели с полем `courses`, содержащим оценку релевантности,
        или None при ошибках.
    """

    logger.info("Оцениваем релевантность опыта работы")

    # Создаём динамическую модель
    try:
        RelevancedSkills = create_pydantic_skills_relevance_matching_model(
            unmatched_vac_list, unmatched_res_list
        )
    except Exception as e:
        logger.error(
            f"Ошибка при создании динамической модели: {str(e)}", exc_info=True
        )
        return None

    # Последняя ошибка
    last_exception = None

    # Для каждой попытки
    for attempt in range(1, MAX_ATTEMPTS + 1):
        logger.info(
            f"Попытка {attempt}/{MAX_ATTEMPTS} для оценки релевантности курсов"
        )

        try:
            # Получаем LLM с увеличивающейся температурой
            structured_llm = get_structured_llm(
                pydantic_model=RelevancedSkills, attempt_number=attempt
            )

            # Формируем входные данные
            prompt_input = {"input": {"pairs": pairs}}

            # Генерируем сообщения
            messages: list[BaseMessage] = await skills_relevance_full_prompt.ainvoke(
                prompt_input
            )

            # Выполняем вызов
            response = await structured_llm.ainvoke(messages)

            logger.info("Успешно оценена релевантность опыта после %d попытки", attempt)
            return response

        except Exception as e:
            last_exception = e
            logger.warning(
                f"Ошибка при попытке {attempt} оценить релевантность опыта: {str(e)}"
            )

            if attempt == MAX_ATTEMPTS:
                break

    # Все попытки провалились
    logger.error(
        f"Все {MAX_ATTEMPTS} попыток оценить релевантность курсов провалились: {str(last_exception)}",
        exc_info=True,
    )
    return None

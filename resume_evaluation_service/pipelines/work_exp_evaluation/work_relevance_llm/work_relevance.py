"""
Функция для создания запроса на оценку релевантности опыта работы с структурированным выводом
с постепенным изменением температуры
"""

from typing import Optional

from langchain_core.messages import BaseMessage
from pydantic import BaseModel

from ....utils.create_llm_with_retries import get_structured_llm
from ....utils.logger import setup_logger
from ..prompts.work_relevance.prompt_builder import work_relevance_full_prompt
from ..pydantic_models.work_relevance import (
    create_pydantic_work_exp_relevance_matching_model,
)

# Логирование
logger = setup_logger(__name__)

# Максимальное количество попыток
MAX_ATTEMPTS = 10


async def evaluate_work_exp_relevance_llm(
    response_work_exp, vacancy: str
) -> Optional[BaseModel]:
    """
    Асинхронно оценивает релевантность опыта работы относительно вакансии.

    Args:
        response_work_exp: Список опыта работы в формате [{"company_name": "...", "position": "..."}, ...]
        vacancy: Текст вакансии (описание должности, требования, обязанности).

    Returns:
        Экземпляр Pydantic-модели с полем `courses`, содержащим оценку релевантности,
        или None при ошибках.
    """

    company_position_list = [
        f"{item.get('company_name')} | {item.get('position')}" for item in response_work_exp.get('work_list')
    ]
    
    print('company_position_list', company_position_list)

    if not company_position_list:
        logger.warning(
            "Список company_position_list пуст — пропускаем оценку релевантности опыта"
        )
        return None

    filtered_work_list = [
        {
            "company_name": item.get('company_name'),
            "position": item.get('position'),
            "work_tasks": item.get('work_tasks'),
        }
        for item in response_work_exp.get('work_list')
    ]
    
    if not filtered_work_list:
        logger.warning(
            "Список filtered_work_list пуст — пропускаем оценку релевантности опыта"
        )
        return None
    
    print('filtered_work_list', filtered_work_list)

    input_llm = {"work_list": filtered_work_list}

    logger.info("Оцениваем релевантность опыта работы")

    # Создаём динамическую модель
    try:
        RelevancedWork = create_pydantic_work_exp_relevance_matching_model(
            company_position_list
        )
    except Exception as e:
        logger.error(
            "Ошибка при создании динамической модели: %s", str(e), exc_info=True
        )
        return None

    last_exception = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        logger.info(
            f"Попытка {attempt}/{MAX_ATTEMPTS} для оценки релевантности курсов"
        )

        try:
            # Получаем LLM с увеличивающейся температурой
            structured_llm = get_structured_llm(
                pydantic_model=RelevancedWork, attempt_number=attempt
            )

            # Формируем входные данные
            prompt_input = {"vacancy": vacancy.strip(), "work_exp": input_llm}

            # Генерируем сообщения
            messages: list[BaseMessage] = await work_relevance_full_prompt.ainvoke(
                prompt_input
            )

            # Выполняем вызов
            response = await structured_llm.ainvoke(messages)

            logger.info(f"Успешно оценена релевантность опыта после {attempt} попытки")
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
        f"Все {MAX_ATTEMPTS} попыток оценить релевантность опыта провалились: {str(last_exception)}",
        exc_info=True,
    )
    return None

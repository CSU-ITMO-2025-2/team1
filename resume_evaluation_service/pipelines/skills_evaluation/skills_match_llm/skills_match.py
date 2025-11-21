"""
Функция для создания запроса для матчинга скиллов из резюме с структурированным выводом
с постепенным изменением температуры
"""

from typing import Optional

from langchain_core.messages import BaseMessage
from pydantic import BaseModel

from ....utils.create_llm_with_retries import get_structured_llm
from ....utils.logger import setup_logger
from ..prompts.skills_match.prompt_builder import skills_match_full_prompt
from ..pydantic_models.skills_match import create_pydantic_skills_agg_match_model

# Логирование
logger = setup_logger(__name__)

# Максимальное количество попыток
MAX_ATTEMPTS = 10


async def skills_match_llm(
    vacancy_skills: list, agg_skills: list
) -> Optional[BaseModel]:
    """
    Создаёт экземпляр LLM, настроенный на структурированный сматченных скилов.
    Температура модели плавно увеличивается с номером попытки, что повышает вероятность
    корректного парсинга при повторных вызовах в случае ошибок (например, из-за "грязных" символов).

    Args:
        vacancy_skills: блок требований из вакансии.
        agg_skills: блок скилов из резюме.

    Returns:
        ChatOpenAI: Экземпляр LLM, привязанный к схеме вывода через `.with_structured_output()`.
    """

    logger.info("Оцениваем релевантность опыта работы")

    # Создаём динамическую модель
    try:
        CategorizedSkill = create_pydantic_skills_agg_match_model(
            vacancy_skills=vacancy_skills, agg_skills=agg_skills
        )
    except Exception as e:
        logger.error(
            "Ошибка при создании динамической модели: %s", str(e), exc_info=True
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
                pydantic_model=CategorizedSkill, attempt_number=attempt
            )

            # Формируем входные данные
            prompt_input = {"vacancy_skills_list": vacancy_skills, "skills": agg_skills}

            # Генерируем сообщения
            messages: list[BaseMessage] = await skills_match_full_prompt.ainvoke(
                prompt_input
            )

            # Выполняем вызов
            response = await structured_llm.ainvoke(messages)

            logger.info(f"Успешно оценена релевантность опыта после {attempt} попытки")
            return response

        except Exception as e:
            last_exception = e
            logger.warning(
                f"Ошибка при попытке {attempt} оценить релевантность опыта: {str(e)}",
            )

            if attempt == MAX_ATTEMPTS:
                break

    # Все попытки провалились
    logger.error(
        f"Все {MAX_ATTEMPTS} попыток оценить релевантность курсов провалились: {str(last_exception)}",
        exc_info=True,
    )
    return None

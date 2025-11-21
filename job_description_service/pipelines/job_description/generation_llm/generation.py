"""
    Функция для создания запроса для генерации описания вакансии с структурированным выводом 
    с постепенным изменением температуры
"""

import asyncio
from typing import Optional

from ....utils.create_llm_with_retries import get_structured_llm
from ....utils.logger import setup_logger
from ..prompts.generation.prompt_builder import (
    generation_full_prompt,
)
from ..pydantic_models.generation import (
    GeneratedVacancyDescription,
)

# Логирование
logger = setup_logger(__name__)

# Максимальное количество попыток
MAX_ATTEMPTS = 10


async def job_generation_llm(
    conditions, education, experience, key_skills, other, position, soft_skills
) -> Optional[GeneratedVacancyDescription]:
    """
    Создаёт экземпляр LLM, настроенный на структурированный вывод описания вакансии.
    Температура модели плавно увеличивается с номером попытки, что повышает вероятность
    корректного парсинга при повторных вызовах в случае ошибок (например, из-за "грязных" символов).

    Args:
        conditions (str): Условия работы.
        education (str): Образование.
        experience (str): Опыт работы.
        key_skills (str): Ключевые навыки.
        other (str): Другие требования.
        position (str): Должность.
        soft_skills (str): Софт-скилы.
        
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
                pydantic_model=GeneratedVacancyDescription, attempt_number=attempt
            )

            # Формируем промпт
            prompt_input = {
                "conditions": conditions,
                "education": education,
                "experience": experience,
                "key_skills": key_skills,
                "other": other,
                "position": position,
                "soft_skills": soft_skills,
            }
            messages = await generation_full_prompt.ainvoke(prompt_input)

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
        f"Все {MAX_ATTEMPTS} попыток спарсить текст провалились: {str(last_exception)}",
        exc_info=True,
    )
    return None


if __name__ == "__main__":
    # Тестовые данные
    conditions = "Офис, график 5/2, командировки по Дальнему Востоку"
    education = "Среднее Специальное, Высшее"
    experience = "1 год"
    key_skills = [
        "Прием и проверка документов",
        "Отработка бухгалтерских и перевозочных документов",
        "Сканирование документов",
        "Обработка запросов контрагента",
        "Работа в 1С: ЭДО; Элар",
        "Архивация документов",
        "Оформление номенклатурных дел",
        "Работа в MS Word, Excel, Outlook",
    ]
    other = (
        "Желателен опыт работы с бухгалтерскими и перевозочными документами, знание делопроизводства; "
        "грамотная речь, пунктуальность, ответственность, организованность, аккуратность, коммуникабельность, "
        "честность и порядочность, объективность, стремление к саморазвитию, способность обрабатывать большой объем информации"
    )
    position = "Специалист отдел обработки документации на бумажном носителе"
    soft_skills = ["Организованность", "Ответственность", "Аккуратность"]

    # Запуск функции
    async def main():
        result = await job_generation_llm(
            conditions=conditions,
            education=education,
            experience=experience,
            key_skills=key_skills,
            other=other,
            position=position,
            soft_skills=soft_skills,
        )
        if result:
            print("Результат парсинга:")
            print(result.model_dump_json())
        else:
            print("Не удалось получить результат после всех попыток.")

    asyncio.run(main())

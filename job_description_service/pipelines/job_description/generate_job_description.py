"""
Функция-обертка для обработки данных и запуска генерации описания вакансии.
"""

import asyncio
from typing import Optional

from utils.clean_text import clean_text
from utils.logger import setup_logger
from pipelines.job_description.generation_llm.generation import job_generation_llm
from pipelines.job_description.pydantic_models.generation import GeneratedVacancyDescription

# Логирование
logger = setup_logger(__name__)

async def get_structured_job_description(
    conditions, education, experience, key_skills, other, position, soft_skills
) -> Optional[GeneratedVacancyDescription]:
    """
    Асинхронно генерирует описание вакансии.

    Args:
        conditions (str): Условия работы.
        education (str): Образование.
        experience (str): Опыт работы.
        key_skills (str): Ключевые навыки.
        other (str): Другие требования.
        position (str): Должность.
        soft_skills (str): Софт-скилы.

    Returns:
        Извлечённые данные или None при ошибке.
    """
    
    # # Проверка на наличие всех входных атрибутов
    # if not conditions or not education or not experience or not key_skills or not other or not position or not soft_skills:
    #     logger.warning("Пустой текст генерации описания вакансии в одном из атрибутов")
    #     return None

    # очищаем текст
    logger.info("Очищаем текст от лишних символов")
    # Очищаем каждую переменную
    cleaned_conditions = clean_text(conditions)
    cleaned_education = clean_text(education)
    cleaned_experience = clean_text(experience)
    cleaned_key_skills = clean_text(key_skills)
    cleaned_other = clean_text(other)
    cleaned_position = clean_text(position)
    cleaned_soft_skills = clean_text(soft_skills)

    try:
        # Запускаем генерацию описания вакансии
        result = await job_generation_llm(
            conditions=cleaned_conditions,
            education=cleaned_education,
            experience=cleaned_experience,
            key_skills=cleaned_key_skills,
            other=cleaned_other,
            position=cleaned_position,
            soft_skills=cleaned_soft_skills,
        )
        
        # Проверяем, что результат не None
        if result is None:
            logger.warning("Результат равен None")
            return {'status': 'failed'}

        # Переводим в словарь
        result_dict = result.model_dump()
        
        # Устанавливаем флаг успешного выполнения
        result_dict['status'] = 'success'
        return result_dict
        
    except Exception as e:
        logger.error(f"Ошибка выполнения: {str(e)}", exc_info=True)
        return {'status': 'failed'}


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
        result = await get_structured_job_description(
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

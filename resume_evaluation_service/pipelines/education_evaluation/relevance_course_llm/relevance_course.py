"""
Функция для создания запроса на оценку релевантности курсов кандидата относительно вакансии с структурированным выводом
с постепенным изменением температуры
"""

import asyncio
import sys
from typing import Dict, List, Optional

from langchain_core.messages import BaseMessage
from pydantic import BaseModel

from utils.create_llm_with_retries import get_structured_llm
from utils.logger import setup_logger
from pipelines.education_evaluation.prompts.course_relevance.course_relevance_prompt_builder import (
    relevance_course_full_prompt,
)
from pipelines.education_evaluation.pydantic_models.course_relevance import create_relevance_course_list_model

# Логирование
logger = setup_logger(__name__)

# Максимальное количество попыток для оценки релевантности курсов
MAX_ATTEMPTS = 10


async def evaluate_courses_relevance_llm(
    courses: List[Dict[str, str]], vacancy: str
) -> Optional[BaseModel]:
    """
    Асинхронно оценивает релевантность курсов кандидата относительно вакансии.

    Args:
        courses: Список курсов в формате [{"course_name": "...", "description": "..."}, ...]
        vacancy: Текст вакансии (описание должности, требования, обязанности).

    Returns:
        Экземпляр Pydantic-модели с полем `courses`, содержащим оценку релевантности,
        или None при ошибках.
    """

    # Извлекаем названия курсов
    course_names = [course.get("course_name", "Без названия") for course in courses]
    logger.info(f"Оцениваем релевантность {len(course_names)} курсов: {course_names}")

    # Создаём динамическую модель данных
    try:
        RelevanceCourseList = create_relevance_course_list_model(course_names)
    except Exception as e:
        logger.error(f"Ошибка при создании динамической модели: {str(e)}", exc_info=True)
        return None

    # Последняя ошибка
    last_exception = None

    # Для каждой попытки
    for attempt in range(1, MAX_ATTEMPTS + 1):
        logger.info(f"Попытка {attempt}/{MAX_ATTEMPTS} для оценки релевантности курсов")

        try:
            # Получаем LLM с увеличивающейся температурой
            structured_llm = get_structured_llm(
                pydantic_model=RelevanceCourseList, attempt_number=attempt
            )

            # Формируем входные данные
            prompt_input = {
                "courses": courses,
                "job_description": vacancy.strip(),
            }

            # Генерируем сообщения
            messages = await relevance_course_full_prompt.ainvoke(
                prompt_input
            )

            # Выполняем вызов
            response = await structured_llm.ainvoke(messages)

            logger.info(f"Успешно оценена релевантность курсов после {attempt} попытки")
            return response

        except Exception as e:
            last_exception = e
            logger.warning(f"Ошибка при попытке {attempt} оценить релевантность курсов: {str(e)}")

            if attempt == MAX_ATTEMPTS:
                break

    # Все попытки провалились
    logger.error(f"Все {MAX_ATTEMPTS} попыток оценить релевантность курсов провалились: {str(last_exception)}")
    
    return None


# === Тестовый запуск ===
if __name__ == "__main__":
    # Пример данных
    SAMPLE_COURSES = [
        {
            "course_name": "Python для анализа данных",
            "description": "Работа с Pandas, NumPy, визуализация в Matplotlib",
        },
        {
            "course_name": "Основы машинного обучения",
            "description": "Обучение моделей на scikit-learn, регрессия, кластеризация",
        },
        {
            "course_name": "Английский для IT",
            "description": "Технический английский, чтение документации",
        },
    ]

    SAMPLE_VACANCY = """
    Вакансия: Data Scientist
    Требования:
    - Знание Python, библиотек для анализа данных (Pandas, NumPy)
    - Опыт в машинном обучении
    - Опыт работы с Jupyter, SQL
    - Английский язык — желательно (на уровне чтения документации)
    """

    async def run_test():
        print("\n🔍 Запуск теста evaluate_courses_relevance_llm\n")
        print("Курсы:")
        for c in SAMPLE_COURSES:
            print(f" - {c['course_name']}: {c['description']}")
        print("\nВакансия:")
        print(SAMPLE_VACANCY)
        print("\n" + "-" * 60)

        try:
            result = await evaluate_courses_relevance_llm(
                SAMPLE_COURSES, SAMPLE_VACANCY
            )
            if result is None:
                print("❌ Не удалось получить результат")
            else:
                print("✅ Успешно получена оценка релевантности:")
                print(result.model_dump_json(indent=2))
        except Exception as e:
            print(f"💥 Ошибка при выполнении теста: {e}")

    # Запуск
    try:
        asyncio.run(run_test())
    except KeyboardInterrupt:
        print("\n⛔ Тест прерван пользователем.")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        sys.exit(1)

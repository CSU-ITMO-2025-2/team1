"""
Финальный runner: извлекает образование → курсы → оценивает релевантность → генерирует отчёт.
"""

import asyncio
import sys
from typing import Any, Dict

from ...utils.logger import setup_logger
from .extract_courses import get_courses
from .extract_edu import get_education
from .get_report import get_report
from .course_relevance import get_courses_relevance

# Логирование
logger = setup_logger(__name__)


async def evaluate_education_match_pipeline(
    resume_text: str, vacancy_text: str
) -> Dict[str, Any]:
    """
    Полный пайплайн:
    1. Извлечение образования и курсов
    2. Оценка релевантности курсов
    3. Генерация полного отчёта

    Returns:
        Полный отчет с оценкой по критериям.
    """
    logger.info("Запуск пайплайна оценки образования и курсов")

    # Параллельно извлекаем образование и курсы
    try:
        resume_edu_task = get_education(resume_text, text_type="резюме")
        vacancy_edu_task = get_education(vacancy_text, text_type="вакансии")
        resume_courses_task = get_courses(resume_text)

        parsing_results = await asyncio.gather(
            resume_edu_task,
            vacancy_edu_task,
            resume_courses_task,
            return_exceptions=True,
        )

        resume_edu, vacancy_edu, resume_courses = parsing_results

    except Exception as e:
        logger.error(
            f"Ошибка при извлечении данных: {str(e)}", exc_info=True
        )
        return {
            "final_score": 0,
            "error": "Ошибка при парсинге образования или курсов",
            "details": str(e),
            "status": "failed"
        }

    # Проверяем что resume_edu не None и статус не "failed"
    if resume_edu is None or resume_edu.get("status") == "failed":
        return {'status': 'failed'}

    # Проверяем что vacancy_edu не None и статус не "failed"
    if vacancy_edu is None or vacancy_edu.get("status") == "failed":
        return {'status': 'failed'}

    # Проверяем что resume_courses не None и статус не "failed"
    if resume_courses is None or resume_courses.get("status") == "failed":
        return {'status': 'failed'}

    # Если курсы найдены, то оценим релевантность
    course_list = resume_courses.get('course_list', [])

    if course_list:

        # Преобразуем курсы
        course_items = [
                    {"course_name": c.get('course_name'), "description": c.get('description')}
                    for c in resume_courses.get('course_list')
                ]
        # Оцениваем релевантность курсов
        try:
            courses_relevance = await get_courses_relevance(course_items, vacancy_text)

            # Процесс получения дополнительной информации
            if courses_relevance is None or courses_relevance.get("status") == "failed":
                return {"status": "failed"}

        except Exception as e:
            logger.error(
                f"Ошибка при оценке релевантности курсов: {str(e)}", exc_info=True
            )
            return {'status': 'failed'}

    else:
        courses_relevance = {'courses': [], 'status': 'success'}


    # print("Courses relevance:", courses_relevance)
    # print("resume_edu:", resume_edu)
    # print("resume_courses:", resume_courses)
    # print("vacancy_edu:", vacancy_edu)
    # Передаём данные в отчёт
    try:
        report = get_report(
            resume_edu=resume_edu,
            vacancy_edu=vacancy_edu,
            resume_courses=resume_courses,
            courses_relevance=courses_relevance
        )
        return report
    except Exception as e:
        logger.error(f"Ошибка при генерации отчёта: {str(e)}", exc_info=True)
        return {'status': 'failed'}

def evaluate_education_match_sync(
    resume_text: str, vacancy_text: str
) -> Dict[str, Any]:
    """Синхронная обёртка."""
    return asyncio.run(evaluate_education_match_pipeline(resume_text, vacancy_text))


if __name__ == "__main__":
    TEST_CASES = [
        {
            "name": "Полное соответствие: высшее + релевантные курсы",
            "resume": """
                Программист
                Образование: высшее, специальность — программная инженерия.
                Курсы:
                - Python для анализа данных
                - Основы машинного обучения
                - Курс по писихологии
                - Курс по дизайну
            """,
            "vacancy": """
                Программист
                Требуется высшее образование в области IT.
                Знание Python и ML обязательно.
            """,
        },
        {
            "name": "Нет образования, но есть релевантные курсы",
            "resume": """
                Без высшего образования.
                Курсы:
                - Python для анализа данных
                - Основы машинного обучения
            """,
            "vacancy": """
            Программист
                Требуется высшее образование в области IT.
                Знание Python и ML обязательно.
            """,
        },
        {
            "name": "Образование не требуется",
            "resume": """
                Опыт работы 5 лет, без формального образования.
            """,
            "vacancy": """
                Образование не требуется. Готовы обучать.
            """,
        },
        {
            "name": "Пустые тексты",
            "resume": "",
            "vacancy": "",
        },
    ]

    async def run_tests():
        print("\n🚀 Запуск тестов evaluate_education_match_pipeline\n")
        for i, case in enumerate(TEST_CASES, 1):
            print(f"--- ТЕСТ {i}: {case['name']} ---")
            print("Резюме:", repr(case["resume"]))
            print("Вакансия:", repr(case["vacancy"]))

            try:
                report = await evaluate_education_match_pipeline(
                    resume_text=case["resume"],
                    vacancy_text=case["vacancy"],
                )

                print(report)
            except Exception as e:
                print(f"💥 Критическая ошибка: {e}")

            print("\n" + "─" * 60 + "\n")
            await asyncio.sleep(1)

    try:
        asyncio.run(run_tests())
    except KeyboardInterrupt:
        print("\n⛔ Тесты прерваны пользователем.")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Критическая ошибка при запуске тестов: {e}")
        sys.exit(1)

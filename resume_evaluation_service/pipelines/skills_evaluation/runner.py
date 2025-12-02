# resume_evaluation_service/pipelines/skills_evaluation/runner.py
"""
Финальный runner: извлекает навыки -> классифицирует -> агрегирует -> сопоставляет -> оценивает -> отчёт.
"""

import asyncio
import sys
from typing import Any, Dict, List, Optional

from utils.logger import setup_logger
from pipelines.skills_evaluation.agg_skills import get_agg_skills
from pipelines.skills_evaluation.classify_skills import get_classify_reqs
from pipelines.skills_evaluation.clean_skills import get_cleaned_skills
from pipelines.skills_evaluation.extract_reqs import get_reqs
from pipelines.skills_evaluation.get_report import get_report
from pipelines.skills_evaluation.resume_parser import get_resume_skills
from pipelines.skills_evaluation.skills_match import get_skills_match
from pipelines.skills_evaluation.skills_relevance import get_skills_relevance

# Настройка логирования
logger = setup_logger(__name__)


async def evaluate_skills_pipeline(
    resume_text: str, vacancy_text: str
) -> Dict[str, Any]:
    """
    Полный асинхронный пайплайн оценки соответствия навыков кандидата вакансии.

    Args:
        resume_text: Текст резюме.
        vacancy_text: Текст вакансии.

    Returns:
        Словарь с финальным отчётом или ошибкой.
    """
    logger.info("Запуск пайплайна оценки навыков")

    try:
        # --- 1. Извлечение текста требований из вакансии ---
        logger.info("Начато извлечение блока требований из вакансии")
        vacancy_requirements_task = get_reqs(vacancy_text)

        # --- 2. Извлечение навыков из резюме ---
        logger.info("Начато извлечение навыков из резюме")
        resume_skills_task = get_resume_skills(resume_text)

        # Параллельное выполнение задач
        parsing_results = await asyncio.gather(
            vacancy_requirements_task,
            resume_skills_task,
            return_exceptions=True,
        )

        vacancy_requirements_data, resume_skills_data = parsing_results

    except Exception as e:
        logger.error(
            f"Ошибка при извлечении данных: {str(e)}", exc_info=True
        )
        return {"status": "failed"}

    # Проверка на наличие ошибок при извлечении требований из вакансии
    if vacancy_requirements_data is None or vacancy_requirements_data.get("status") == "failed":
        logger.error("Не удалось извлечь требования в вакансии")
        return {"status": "failed"}

    # Проверка на наличие ошибок при извлечении навыков из резюме
    if resume_skills_data is None or resume_skills_data.get("status") == "failed":
        logger.error("Не удалось извлечь навыки из резюме")
        return {"status": "failed"}

    # --- 3. Классификация требований вакансии на must_have/nice_to_have ---
    try:
        logger.info("Начата классификация требований вакансии")
        vacancy_skills_data = await get_classify_reqs(
            vacancy_requirements_data.get('requirements_text')
        )

    except Exception as e:
        logger.error(
            f"Ошибка при извлечении данных: {str(e)}", exc_info=True
        )
        return {"status": "failed"}

    # Проверка на наличие ошибок при классификации требований вакансии
    if vacancy_skills_data is None or vacancy_skills_data.get("status") == "failed":
        logger.error("Не удалось классифицировать требования")
        return {"status": "failed"}

    # --- 4. Очистка и нормализация навыков из резюме ---
    try:
        # Передаем список всех навыков из вакансии
        vacancy_skills_list = vacancy_skills_data.get('must_have_skills') + vacancy_skills_data.get('nice_to_have_skills')
        logger.info("Начата очистка и нормализация навыков из резюме")
        cleaned_vacancy_skills = await get_cleaned_skills(
            vacancy_skills_list
        )

    except Exception as e:
        logger.error(
            f"Ошибка при извлечении данных: {str(e)}", exc_info=True
        )
        return {"status": "failed"}


    # Проверка на наличие ошибок нормализации навыков вакансии
    if cleaned_vacancy_skills is None or cleaned_vacancy_skills.get("status") == "failed":
        logger.error("Не удалось нормализовать навыки вакансии")
        return {"status": "failed"}

    # Категории, которые мы допускаем к проверке
    verifiable_categories = {
        "Технология/инструмент",
        "Язык программирования",
        "Язык",
        "Стандарт/методология",
        "Деловой навык",
        "Процессный навык"
    }

    # Проставляем флаг на скилы, которые мы будем проверять
    for skill in cleaned_vacancy_skills.get('skills'):
        skill['is_verifiable'] = skill.get('category') in verifiable_categories

    # Верифицированные навыки
    verifiable_skills = [skill.get('skill_name') for skill in cleaned_vacancy_skills.get('skills') if skill.get('is_verifiable')]

    # --- 5. Стандартизация игрегация навыков вакансии ---

    try:
        logger.info("Начата стандартизация навыков вакансии")
        aggregated_vacancy_skills = await get_agg_skills( # Передаем только верифицированные навыки
            verifiable_skills
        )
    except Exception as e:
        logger.error(
            f"Ошибка при извлечении данных: {str(e)}", exc_info=True
        )
        return {"status": "failed"}

    # Проверка на наличие ошибок стандартизации навыков вакансии
    if aggregated_vacancy_skills is None or aggregated_vacancy_skills.get("status") == "failed":
        logger.error("Не удалось стандартизировать навыки вакансии")
        return {"status": "failed"}

    # --- 6. Сопоставление навыков со стандартизованным названием ---
    try:
        logger.info("Начинаем матчить навыки с оригинальными названиями")
        matched_vacancy_skills = await get_skills_match(
            verifiable_skills,
            aggregated_vacancy_skills.get('skills')
        )
    except Exception as e:
        logger.error(
            f"Ошибка при извлечении данных: {str(e)}", exc_info=True
        )
        return {"status": "failed"}

    # Проверка на наличие ошибок сопоставления навыков вакансии
    if matched_vacancy_skills is None or matched_vacancy_skills.get("status") == "failed":
        logger.error("Не удалось сопоставить навыки вакансии")
        return {"status": "failed"}

    # Справочник для сопоставления навыков с категориями
    name_to_category = {
            skill['original_name']: skill['category']
            for skill in matched_vacancy_skills['skills']
        }

    # --- 7. Пробуем прямо сопоставить навыки с резюме ---

    # Приводим навыки к нижнему регистру
    resume_skills_list = [skill.lower() for skill in resume_skills_data.get('skills')]

    # Сматченные напрямую навыки
    current_match =  [s for s in list(set(name_to_category.values())) if s.lower() in resume_skills_list]

    # Несматченные напрямую навыки
    current_unmatched_skills = [s for s in list(set(name_to_category.values())) if s not in current_match]
    print('current_unmatched_resume_skills', current_unmatched_skills)
    print('current_match', current_match)

    # --- 8. Оценка релевантности оставшихся навыков

    def get_all_pairs(vacancy_skills: list, resume_skills: list):
        '''Возвращает все возможные пары навыков между вакансии и резюме'''
        pairs = []

        for v_skill in vacancy_skills:
            for r_skill in resume_skills:
                pairs.append({
                    "vacancy_skill": v_skill,
                    "resume_skill": r_skill
                })

        return pairs

    pairs = get_all_pairs(current_unmatched_skills,resume_skills_list)
    print(pairs)

    try:
        logger.info("Начинаем оценивать релевантность оставшихся навыков")
        unmatched_vacancy_skills_relevance = await get_skills_relevance(
            current_unmatched_skills,
            resume_skills_list,
            pairs
        )
    except Exception as e:
        logger.error(
            f"Ошибка при извлечении данных: {str(e)}", exc_info=True
        )
        return {"status": "failed"}

    # Проверка на наличие ошибок сопоставления навыков вакансии
    if unmatched_vacancy_skills_relevance is None or unmatched_vacancy_skills_relevance.get("status") == "failed":
        logger.error("Не удалось сопоставить навыки вакансии")
        return {"status": "failed"}



    # --- 9. Генерация финального отчёта ---
    logger.info("Генерация финального отчёта по навыкам")
    try:
        final_report = get_report(
            resume_skills_data,
            vacancy_skills_data,
            aggregated_vacancy_skills,
            name_to_category,
            current_match,
            current_unmatched_skills,
            unmatched_vacancy_skills_relevance
        )
        logger.info("Пайплайн оценки навыков завершён успешно")
        return final_report
    except Exception as e:
        logger.error(f"Ошибка при генерации отчёта: {e}", exc_info=True)
        return {"error": f"Ошибка при генерации отчёта: {e}", "evaluation": None}


def evaluate_skills_pipeline_sync(
    resume_text: str, vacancy_text: str
) -> Dict[str, Any]:
    """Синхронная обёртка для пайплайна оценки навыков."""
    return asyncio.run(evaluate_skills_pipeline(resume_text, vacancy_text))


# === Тестовый запуск через if __name__ == "__main__" ===
if __name__ == "__main__":
    # Примеры тестовых данных (упрощённые)
    TEST_RESUME = """
    Резюме: Python-разработчик
    Навыки:
    - Python 3+
    - Django Framework
    - DRF
    - FastAPI
    - PostgreSQL
    - Docker
    - ООП
    - Паттерны проектирования
    - Git
    - Linux
    - Английский B1
    - эмоциональный интеллект
    - коммуникабельность
    - лидерство
    - Коммуникабельность
    """

    TEST_VACANCY = """
    Вакансия: Middle Python-разработчик
    Обязанности:
    - Разработка и поддержка backend-сервисов
    Требования:
    - Опыт работы с Python 3.6 от 2 лет
    - Знание Django, DRF
    - Знание Фреймворков Python
    - Понимание принципов ООП
    - Опыт работы с PostgreSQL
    - Знание Docker
    - Навыки работы с Git
    - gitlab
    - контейнеризация
    - Умение писать тесты (pytest)
    - Доброжелательность
    - Хорошесть
    - Коммуникабельность
    nice to have:
    - Опыт с FastAPI
    - Знание Redis
    - Английский B2
    - Лидерство
    """

    async def run_test():
        print("\n🚀 Запуск теста evaluate_skills_pipeline\n")
        print("Резюме (пример):")
        print(TEST_RESUME[:200] + "...")
        print("\nВакансия (пример):")
        print(TEST_VACANCY[:100] + "...")
        print("-" * 60)

        try:
            report = await evaluate_skills_pipeline(TEST_RESUME, TEST_VACANCY)
            print("\nОтчет:")
            print(report)

        except Exception as e:
            print(f"💥 Критическая ошибка при выполнении теста: {e}")

    try:
        asyncio.run(run_test())
    except KeyboardInterrupt:
        print("\n⛔ Тест прерван пользователем.")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Критическая ошибка при запуске тестов: {e}")
        sys.exit(1)

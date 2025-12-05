"""
Финальный runner: извлекает зарплату → сравнивает → возвращает отчёт.
"""

import asyncio
from typing import Any, Dict

from utils.logger import setup_logger
from pipelines.salary_evaluation.extract_sales import get_salary
from pipelines.salary_evaluation.get_report import compare_salaries

# Логирование
logger = setup_logger(__name__)

async def evaluate_salary_match(resume_text: str, vacancy_text: str) -> Dict[str, Any]:
    """
    Полный пайплайн: извлечение + сравнение + отчёт.
    """

    # Параллельно извлекаем зарплату из резюме и вакансии
    logger.info("Извлекаем текст из резюме")
    resume_task = get_salary(resume_text, text_type="резюме")
    logger.info("Извлекаем текст из вакансии")
    vacancy_task = get_salary(vacancy_text, text_type="вакансии")

    try:
        resume_data, vacancy_data = await asyncio.gather(resume_task, vacancy_task)
    except Exception as e:
        return {
            "score": 0,
            "message": f"Ошибка при извлечении: {str(e)}",
            "resume_salary": None,
            "resume_text": None,
            "vacancy_salary": None,
            "vacancy_text": None,
            "deviation_percent": None,
            "status": "failed"
        }
        
    # Проверка статуса resume_data
    if resume_data is None or resume_data.get("status") == "failed":
        logger.error("Ошибка: Не удалось извлечь зарплатные ожидания из входного текста")
        return {
            "score": 0,
            "message": "Ошибка: Не удалось извлечь зарплатные ожидания из резюме",
            "resume_salary": None,
            "resume_text": None,
            "vacancy_salary": None,
            "vacancy_text": None,
            "deviation_percent": None,
            "status": "failed"
        }
    
    # Проверка статуса vacancy_data
    if vacancy_data is None or vacancy_data.get("status") == "failed":
        logger.error("Ошибка: Не удалось извлечь зарплатные ожидания из вакансии")
        return {
            "score": 0,
            "message": "Ошибка: Не удалось извлечь зарплатные ожидания из вакансии",
            "resume_salary": None,
            "resume_text": None,
            "vacancy_salary": None,
            "vacancy_text": None,
            "deviation_percent": None,
            "status": "failed"
        }

    # Генерируем отчёт
    report = compare_salaries(resume_salary=resume_data, vacancy_salary=vacancy_data)

    return report


def evaluate_salary_match_sync(
    resume_text: str, vacancy_text: str
) -> Dict[str, Any]:
    """Синхронная обёртка."""
    return asyncio.run(evaluate_salary_match(resume_text, vacancy_text))



# Локальные тесты
if __name__ == "__main__":
    """Тестирование модуля извлечения и сравнения зарплат."""

    import json
    from pprint import pprint

    # Настройка логирования для тестов
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("=" * 80)
    print("ТЕСТИРОВАНИЕ МОДУЛЯ SALARY EVALUATION")
    print("=" * 80)

    # Тестовые случаи
    test_cases = [
        {
            "name": "Тест 1: Зарплата в резюме ниже вакансии",
            "resume": """
                Иванов Иван Иванович
                Python Developer
                Опыт работы: 5 лет
                Ожидаемая зарплата: 150 000 руб.
                Навыки: Python, Django, PostgreSQL
            """,
            "vacancy": """
                Вакансия: Senior Python Developer
                Компания: ТехноСофт
                Зарплата: от 180 000 до 220 000 руб.
                Требования: Python 3.9+, Django, PostgreSQL
            """
        },
        {
            "name": "Тест 2: Зарплата в резюме выше вакансии",
            "resume": """
                Петров Петр
                Frontend Developer
                Зарплатные ожидания: от 250 тыс. рублей
                Навыки: React, TypeScript, Node.js
            """,
            "vacancy": """
                Ищем Frontend разработчика
                Зарплата до 180000 рублей
                Офис в центре Москвы
            """
        },
        {
            "name": "Тест 3: Зарплата не указана в резюме",
            "resume": """
                Сидоров Сидор
                Data Scientist
                Опыт работы с ML моделями
                Python, TensorFlow, PyTorch
            """,
            "vacancy": """
                Data Scientist в стартап
                Зарплата: 200-300 тыс. руб.
                Удаленная работа
            """
        },
        {
            "name": "Тест 4: Зарплата не указана в вакансии",
            "resume": """
                DevOps инженер
                Ожидания по зарплате: 220000 руб.
                Kubernetes, Docker, AWS
            """,
            "vacancy": """
                DevOps Engineer
                Зарплата по договоренности
                Требуется опыт с облачными технологиями
            """
        },
        {
            "name": "Тест 5: Зарплата не указана нигде",
            "resume": """
                Backend разработчик
                Java, Spring Boot
                Ищу интересные проекты
            """,
            "vacancy": """
                Java Developer
                Работа в крупной компании
                Конкурентная зарплата
            """
        },
        {
            "name": "Тест 6: Зарплата в долларах",
            "resume": """
                Senior Developer
                Минимальная зарплата: $3000
                Remote work only
            """,
            "vacancy": """
                Remote Senior Developer
                Salary: up to $4500
                Full-time position
            """
        },
        {
            "name": "Тест 7: Диапазоны частично пересекаются",
            "resume": """
                QA Engineer
                Зарплатные ожидания: 120-150 тысяч рублей
            """,
            "vacancy": """
                Тестировщик ПО
                ЗП: от 100 до 130 тыс. руб.
            """
        }
    ]

    # Запуск тестов
    async def run_tests():
        print("\nЗапуск тестов...\n")

        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{'='*60}")
            print(f"{test_case['name']}")
            print('='*60)

            try:
                result = await evaluate_salary_match(
                    resume_text=test_case["resume"],
                    vacancy_text=test_case["vacancy"]
                )

                print(f"\n📊 Результат:")
                print(f"Тест кейс: {test_case}")
                print(f"Результат: {result}")
            except Exception as e:
                print(f"❌ Ошибка в тесте: {str(e)}")
                import traceback
                traceback.print_exc()

    # Запуск асинхронных тестов
    asyncio.run(run_tests())

    print("\n" + "="*80)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("="*80)

"""
Финальный runner: извлекает дополнительную информацию → сравнивает → возвращает отчёт.
"""

import asyncio
import sys
from typing import Any, Dict

from ...utils.logger import setup_logger
from .additional_info import get_additional_info

# Логирование
logger = setup_logger(__name__)


async def evaluate_additional_match(
    resume_text: str, vacancy_text: str
) -> Dict[str, Any]:
    """
    Полный пайплайн: извлечение дополнительной информации → сравнение → отчёт.

    Args:
        resume_text: Текст резюме
        vacancy_text: Текст вакансии

    Returns:
        Словарь с отчётом о соответствии графика работы и тд.
    """
    logger.info("Запуск пайплайна оценки дополнительной информации")

    try:
        result = await get_additional_info(resume_text, vacancy_text)
        
        # Процесс получения дополнительной информации
        if result is None or result.get("status") == "failed":
            return {
                'vacancy_schedule': {
                    'schedule': [],
                    'details': ''
                },
                'resume_schedule': {
                    'schedule': [],
                    'details': ''
                },
                'match': False,
                'reason': 'Не удалось извлечь данные о графике работы',
                'score': 0,
                'status': 'failed'
            }
        
        # Добавляем score и статус
        result['score'] = 5 if result.get('match', False) else 0
        result['status'] = 'success'
        return result
        
    except Exception as e:
        logger.error(
            f"Ошибка при оценке дополнительной информации: {str(e)}", exc_info=True
        )
        return {
            'status': 'failed',
            'vacancy_schedule': {
                'schedule': [],
                'details': ''
            },
            'resume_schedule': {
                'schedule': [],
                'details': ''
            },
            'match': False,
            'reason': 'Не удалось извлечь данные о графике работы',
            'score': 0,
            'status': 'failed'
        }

def evaluate_additional_match_sync(
    resume_text: str, vacancy_text: str
) -> Dict[str, Any]:
    """Синхронная обёртка."""
    return asyncio.run(evaluate_additional_match(resume_text, vacancy_text))


# === Тестовый запуск через if __name__ == "__main__" ===
if __name__ == "__main__":
    """
    Простой тест модуля additional_evaluation.
    Проверяет 3 основных сценария: совпадение, несовпадение и отсутствие данных.
    """

    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ МОДУЛЯ ADDITIONAL_EVALUATION")
    print("="*60 + "\n")

    TEST_CASES = [
        {
            "name": "Тест 1: ✅ Полное совпадение (удаленка)",
            "resume": """
                Python Developer
                Ищу удаленную работу
                График: полный день
            """,
            "vacancy": """
                Вакансия: Python Developer
                График: удаленная работа
                Полная занятость
            """,
            "expected": "match"
        },
        {
            "name": "Тест 2: ❌ Несовпадение (офис vs удаленка)",
            "resume": """
                Ищу только удаленную работу
                В офис не готов
            """,
            "vacancy": """
                Требуется работа в офисе 5/2
                Удаленка не предусмотрена
                Москва, м. Белорусская
            """,
            "expected": "no_match"
        },
        {
            "name": "Тест 3: ❓ График не указан",
            "resume": """
                Frontend Developer
                React, TypeScript, 5 лет опыта
            """,
            "vacancy": """
                Ищем Frontend разработчика
                Зарплата от 200 000 руб
            """,
            "expected": "default_match"
        }
    ]

    async def run_tests():
        print("Запуск тестов...\n")

        for i, test in enumerate(TEST_CASES, 1):
            print(f"{test['name']}")
            print("-" * 40)

            try:
                # Запускаем функцию
                result = await evaluate_additional_match(
                    resume_text=test["resume"],
                    vacancy_text=test["vacancy"]
                )
                print(f"Результат: {result}")

                # Проверяем результат
                if "match" in result:
                    if result["match"]:
                        print(f"Результат: ✅ Соответствует")
                    else:
                        print(f"Результат: ❌ Не соответствует")

                # Показываем причину
                if "reason" in result:
                    print(f"Причина: {result['reason']}")

                # Показываем извлеченные графики
                if "vacancy_schedule" in result and result["vacancy_schedule"]:
                    schedules = result["vacancy_schedule"].get("schedules", [])
                    if schedules:
                        print(f"График вакансии: {', '.join(schedules)}")

                if "resume_schedule" in result and result["resume_schedule"]:
                    schedules = result["resume_schedule"].get("schedules", [])
                    if schedules:
                        print(f"График резюме: {', '.join(schedules)}")

                # Проверка ожидаемого результата
                if test["expected"] == "match" and result.get("match") == True:
                    print("✅ Тест пройден")
                elif test["expected"] == "no_match" and result.get("match") == False:
                    print("✅ Тест пройден")
                elif test["expected"] == "default_match" and result.get("match") == True:
                    print("✅ Тест пройден (по умолчанию)")
                else:
                    print("⚠️ Неожиданный результат")

            except Exception as e:
                print(f"❌ Ошибка: {str(e)}")

            print("\n")

    # Запускаем тесты
    try:
        asyncio.run(run_tests())
        print("="*60)
        print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
        print("="*60)
    except KeyboardInterrupt:
        print("\n⛔ Тесты прерваны")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")

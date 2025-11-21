"""
Функция-обертка, которая обрабатывает входной текст и запускает процесс парсинга уровня образования.
"""

from typing import Optional

from ...pipelines.education_evaluation.extract_main_edu_llm.extract_edu import (
    extract_main_edu_llm,
)
from ...utils.clean_text import clean_text
from ...utils.logger import setup_logger

# Логирование
logger = setup_logger(__name__)


async def get_education(text: str, text_type: str) -> dict:
    """
    Асинхронно извлекает данные об образовании.

    Args:
        text (str): Текст вакансии или резюме.
        text_type (str): Тип текста — "вакансия" или "резюме".

    Returns:
        Извлечённые данные или None при ошибке.
    """
    # Проверяем, что текст не пустой
    if not text or not text.strip():
        logger.warning("Пустой текст для извлечения образования (тип: %s)", text_type)
        return {"status": "failed"}

    # Проверяем, что тип текста корректный
    if text_type not in ["вакансии", "резюме"]:
        logger.warning("Неверный тип текста для извлечения зарплаты (тип: %s)", text_type)
        return {"status": "failed"}


    # очищаем текст
    logger.info(f"Очищаем текст от лишних символов для {text_type}")
    cleaned_text = clean_text(text)
    logger.info(f"Текст очищен для {text_type}")

    try:
        result = await extract_main_edu_llm(cleaned_text, text_type=text_type)
        
        # Проверяем, что результат не None
        if result is None:
            logger.error("Результат равен None")
            return {'status': 'failed'}

        # Переводим в словарь
        result_dict = result.model_dump()

        # Устанавливаем флаг успешного выполнения
        result_dict['status'] = 'success'
        return result_dict
        
    except Exception as e:
        logger.error(f"Ошибка выполнения для {text_type}: %s", str(e), exc_info=True)
        return {"status": "failed"}




# === Тестовый запуск через if __name__ == "__main__" ===
if __name__ == "__main__":
    """
    Простой тест модуля get_education.
    Проверяет 3 основных сценария: извлечение из резюме, извлечение из вакансии и обработку ошибок.
    """
    import asyncio
    from unittest.mock import AsyncMock, patch
    
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ МОДУЛЯ GET_EDUCATION")
    print("="*60 + "\n")

    TEST_CASES = [
        {
            "name": "Тест 1: ✅ Извлечение образования из резюме",
            "text": """
                Образование:
                - МГУ им. М.В. Ломоносова, 2015-2020
                  Факультет: Вычислительной математики и кибернетики
                  Специальность: Прикладная математика и информатика
                  Диплом с отличием
                
                - Курсы повышения квалификации
                  Machine Learning, Coursera, 2021
            """,
            "text_type": "резюме",
            "expected": "success"
        },
        {
            "name": "Тест 2: ✅ Извлечение требований к образованию из вакансии",
            "text": """
                Требования:
                - Высшее техническое образование (IT, математика, физика)
                - Желательно профильное образование в области Computer Science
                - Приветствуются сертификаты и курсы по машинному обучению
            """,
            "text_type": "вакансии",
            "expected": "success"
        },
        {
            "name": "Тест 3: ❌ Пустой текст",
            "text": "",
            "text_type": "резюме",
            "expected": "failed"
        },
        {
            "name": "Тест 4: ❌ Неверный тип текста",
            "text": "Какой-то текст про образование",
            "text_type": "неверный_тип",
            "expected": "failed"
        }
    ]

    async def run_tests():
        print("Запуск тестов...\n")

        for i, test in enumerate(TEST_CASES, 1):
            print(f"{test['name']}")
            print("-" * 40)

            try:
                # Для успешных кейсов мокаем extract_main_edu_llm
                if test["expected"] == "success":
                    # Создаем мок результата
                    from types import SimpleNamespace
                    mock_result = SimpleNamespace()
                    mock_result.model_dump = lambda: {
                        "edu_list": [
                            {
                                "level": "Высшее",
                                "specialization": ["Техническое", "Инженерное"]
                            }
                        ]
                    }
                    
                    # Патчим функцию extract_main_edu_llm
                    with patch('__main__.extract_main_edu_llm', new_callable=AsyncMock) as mock_extract:
                        mock_extract.return_value = mock_result
                        
                        # Запускаем функцию
                        result = await get_education(
                            text=test["text"],
                            text_type=test["text_type"]
                        )
                else:
                    # Для ошибочных кейсов запускаем как есть
                    result = await get_education(
                        text=test["text"],
                        text_type=test["text_type"]
                    )

                print(f"Результат: {result}")

                # Проверяем статус
                if "status" in result:
                    if result["status"] == "success":
                        print(f"Статус: ✅ Успешно")
                        
                        # Показываем извлеченное образование
                        if "edu_list" in result:
                            for edu in result["edu_list"]:
                                print(f"  - Уровень: {edu.get('level', 'Не указано')}")
                                specs = edu.get('specialization', [])
                                if specs:
                                    print(f"    Специализация: {', '.join(specs)}")
                    else:
                        print(f"Статус: ❌ Ошибка")

                # Проверка ожидаемого результата
                if test["expected"] == result.get("status"):
                    print("✅ Тест пройден")
                else:
                    print(f"⚠️ Неожиданный результат (ожидался статус: {test['expected']})")

            except Exception as e:
                print(f"❌ Ошибка: {str(e)}")
                if test["expected"] == "failed":
                    print("✅ Тест пройден (ожидалась ошибка)")

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
salary_extraction_examples = [
    {
        "input": """Вакансия: Python-разработчик
Зарплата: от 150 000 до 220 000 руб. на руки
Требования: Python 3.9+, Django, PostgreSQL""",
        "output": {
            "min_amount": 150000,
            "max_amount": 220000,
            "is_specified": True,
            "extracted_text": "от 150 000 до 220 000 руб.",
        },
    },
    {
        "input": """Резюме: Middle Python Developer
до 250 тыс. рублей
Навыки: Python, Flask, MongoDB""",
        "output": {
            "min_amount": None,
            "max_amount": 250000,
            "is_specified": True,
            "extracted_text": "до 250 тыс. рублей",
        },
    },
    {
        "input": """Вакансия: Data Scientist
Условия: ЗП до 3500$ после испытательного срока
Требования: Python, Pandas, SQL""",
        "output": {
            "min_amount": None,
            "max_amount": 3500,
            "is_specified": True,
            "extracted_text": "до 3500$",
        },
    },
    {
        "input": """Резюме: Frontend Developer
Компенсационные ожидания: по договорённости
Навыки: React, TypeScript""",
        "output": {
            "min_amount": None,
            "max_amount": None,
            "is_specified": False,
            "extracted_text": "по договорённости",
        },
    },
    {
        "input": """Вакансия: DevOps Engineer
Зарплата: от 200000 рублей gross
Требования: Kubernetes, AWS, CI/CD""",
        "output": {
            "min_amount": 200000,
            "max_amount": None,
            "is_specified": True,
            "extracted_text": "от 200000 рублей gross",
        },
    },
    {
        "input": """Вакансия: экономист
Зарплата: до 100000 рублей gross
Требования: бухгалтерский учет""",
        "output": {
            "min_amount": None,
            "max_amount": 100000,
            "is_specified": True,
            "extracted_text": "до 100000 рублей gross",
        },
    },
]

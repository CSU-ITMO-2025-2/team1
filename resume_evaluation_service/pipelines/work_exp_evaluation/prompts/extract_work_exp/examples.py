work_experience_examples = [
    {
        "input": "Опыт работы:\n1. Яндекс (2020-2022) - Разработчик Python\n- Разработка API\n- Оптимизация БД\n2. Google (2022-н.в.) - Senior Developer",
        "output": {
            "work_list": [
                {
                    "company_name": "Яндекс",
                    "position": "Разработчик Python",
                    "work_tasks": "Разработал API, оптимизировал БД",
                    "start_date": "2020-01-01",
                    "end_date": "2022-12-01",
                    "duration": "2 года 12 месяцев",
                    "currently_working": False,
                },
                {
                    "company_name": "Google",
                    "position": "Senior Developer",
                    "work_tasks": "Развивал ключевые компоненты платформы",
                    "start_date": "2022-01-01",
                    "end_date": None,
                    "duration": None,
                    "currently_working": True,
                },
            ],
            "full_work_exp_years": None,
            "work_exp_month_after_year": None,
        },
    },
    {
        "input": "Работал в ООО 'Рога и Копыта' с января 2018 по май 2020 (2 года 4 месяца) на должности менеджера по продажам. Обязанности:\n- Ведение переговоров\n- Заключение договоров",
        "output": {
            "work_list": [
                {
                    "company_name": "Рога и Копыта",
                    "position": "Менеджер по продажам",
                    "work_tasks": "Вёл переговоры с клиентами, заключал коммерческие договоры",
                    "start_date": "2018-01-01",
                    "end_date": "2020-05-01",
                    "duration": "2 года 4 месяца",
                    "currently_working": False,
                }
            ],
            "full_work_exp_years": 2,
            "work_exp_month_after_year": 4,
        },
    },
    {
        "input": "Фриланс проекты (2019-2021):\n- Разработка сайта для клиента X\n- Создание мобильного приложения",
        "output": {
            "work_list": [
                {
                    "company_name": "Freelance (Клиент: X)",
                    "position": "Web Developer",
                    "work_tasks": "Разработал сайт для клиента X, создал мобильное приложение",
                    "start_date": "2019-01-01",
                    "end_date": "2021-12-01",
                    "duration": "2 года 11 месяцев",
                    "currently_working": False,
                }
            ],
            "full_work_exp_years": 2,
            "work_exp_month_after_year": 11,
        },
    },
    {
        "input": "Требования к кандидату:\n- Опыт работы от 3 лет в должности Python Developer\n- Знание Django, Flask",
        "output": {
            "work_list": [
                {
                    "company_name": None,
                    "position": "Python Developer",
                    "work_tasks": "Знание Django, Flask",
                    "start_date": None,
                    "end_date": None,
                    "duration": "3 года",
                    "currently_working": False,
                }
            ],
            "full_work_exp_years": 3,
            "work_exp_month_after_year": 0,
        },
    },
    {
        "input": "Нет опыта работы",
        "output": {
            "work_list": [],
            "full_work_exp_years": 0,
            "work_exp_month_after_year": 0,
        },
    },
]

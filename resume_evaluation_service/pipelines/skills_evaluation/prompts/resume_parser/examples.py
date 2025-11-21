resume_parsing_examples = [
    {
        "input": """Резюме: Python-разработчик

        Опыт работы:
        - Разработка серверной части веб-приложений на Python 3.9+
        - Использование Django и PostgreSQL
        - Настройка Docker-контейнеров
        
        Навыки:
        - Python, Django, Flask
        - PostgreSQL, Redis
        - Docker, Kubernetes
        - Английский B2""",
        "output": '{"skills":["Python", "Django", "Flask", "PostgreSQL", "Redis", "Docker", "Kubernetes", "Английский B2"]}',
    },
    {
        "input": """Резюме: Аналитик данных

        Ключевые навыки:
        - Анализ данных в Excel (сводные таблицы, макросы)
        - Визуализация данных: Power BI, Tableau
        - Языки: SQL, Python (pandas, numpy)
        - Английский C1""",
        "output": '{"skills":["Excel", "Power BI", "Tableau", "SQL", "Python", "pandas", "numpy", "Английский C1"]}',
    },
    {
        "input": """Резюме: Менеджер проектов

        Профессиональные компетенции:
        - Управление проектами в Jira, Confluence
        - Методологии: Agile, Scrum, Kanban
        - Сертификация PMP
        - Немецкий B1""",
        "output": '{"skills":["Jira", "Confluence", "Agile", "Scrum", "Kanban", "PMP", "Немецкий B1"]}',
    },
    {
        "input": """Резюме: Бухгалтер

        Навыки:
        - 1С:Бухгалтерия 8.3
        - Налоговый и бухгалтерский учет
        - Подготовка отчетности по МСФО
        - Продвинутый Excel (VBA)""",
        "output": '{"skills":["1С:Бухгалтерия", "Налоговый учёт", "Бухгалтерский учёт", "МСФО", "Excel", "VBA"]}',
    },
    {
        "input": """Резюме: Логист

        Профессиональные навыки:
        - Работа с WMS-системами (SAP WM, 1C:Логистика)
        - Оптимизация логистических процессов
        - Владение английским на уровне Intermediate
        - Продвинутый пользователь Excel""",
        "output": '{"skills":["WMS", "SAP WM", "1C:Логистика", "Английский B1", "Excel"]}',
    },
    {
        "input": """Резюме: Экономист

        Квалификация:
        - Финансовый анализ и моделирование
        - Продвинутый Excel (Power Query, Power Pivot)
        - Языки программирования: Python (pandas), R
        - Английский для бизнеса""",
        "output": '{"skills":["Финансовый анализ", "Финансовое моделирование", "Excel", "Power Query", "Power Pivot", "Python", "pandas", "R", "Английский B2"]}',
    },
    {
        "input": """Резюме: Системный администратор

        Технические навыки:
        - Администрирование Windows/Linux серверов
        - Виртуализация: VMware, Hyper-V
        - Сети: Cisco IOS, TCP/IP, DNS, DHCP
        - Английский для технической документации""",
        "output": '{"skills":["Windows Server", "Linux", "VMware", "Hyper-V", "Cisco IOS", "TCP/IP", "DNS", "DHCP", "Английский B2"]}',
    },
]

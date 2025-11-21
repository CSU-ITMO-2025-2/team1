skill_relevance_examples = [
    {
        "input": {
            "pairs": [
                {"vacancy_skill": "oop", "resume_skill": "Python"},
                {"vacancy_skill": "oop", "resume_skill": "Django Framework"},
                {"vacancy_skill": "oop", "resume_skill": "DRF"},
                {"vacancy_skill": "oop", "resume_skill": "FastAPI"},
                {"vacancy_skill": "oop", "resume_skill": "PostgreSQL"},
                {"vacancy_skill": "oop", "resume_skill": "ElasticSearch"},
                {"vacancy_skill": "oop", "resume_skill": "Celery"},
                {"vacancy_skill": "oop", "resume_skill": "Git"},
                {"vacancy_skill": "oop", "resume_skill": "Nginx"},
                {"vacancy_skill": "oop", "resume_skill": "Linux"},
                {"vacancy_skill": "oop", "resume_skill": "Docker"},
                {"vacancy_skill": "oop", "resume_skill": "k8s"},
                {"vacancy_skill": "oop", "resume_skill": "Gunicorn"},
                {"vacancy_skill": "oop", "resume_skill": "RabbitMQ"},
                {"vacancy_skill": "oop", "resume_skill": "Jenkins"},
                {"vacancy_skill": "oop", "resume_skill": "Gitlab CI"},
                {"vacancy_skill": "oop", "resume_skill": "HTML"},
                {"vacancy_skill": "oop", "resume_skill": "CSS"},
                {"vacancy_skill": "oop", "resume_skill": "JavaScript"},
                {"vacancy_skill": "oop", "resume_skill": "TypeScript"},
                # Полная аналогичность
                {
                    "vacancy_skill": "oop",
                    "resume_skill": "объектно-ориентированное программирование",
                },
                {"vacancy_skill": "oop", "resume_skill": "парадигма ООП"},
                # Частичная аналогичность
                {"vacancy_skill": "oop", "resume_skill": "наследование"},
                {"vacancy_skill": "oop", "resume_skill": "инкапсуляция"},
                {"vacancy_skill": "oop", "resume_skill": "полиморфизм"},
                {"vacancy_skill": "oop", "resume_skill": "абстракция"},
            ]
        },
        "output": {
            "pairs": [
                # Полная аналогичность
                {
                    "vacancy_skill": "oop",
                    "resume_skill": "объектно-ориентированное программирование",
                    "reason": "Прямое совпадение термина",
                    "relevance": "Полная аналогичность",
                },
                {
                    "vacancy_skill": "oop",
                    "resume_skill": "парадигма ООП",
                    "reason": "Синонимичное описание парадигмы",
                    "relevance": "Полная аналогичность",
                },
                # Частичная аналогичность
                {
                    "vacancy_skill": "oop",
                    "resume_skill": "наследование",
                    "reason": "Элемент парадигмы ООП",
                    "relevance": "Частичная аналогичность",
                },
                {
                    "vacancy_skill": "oop",
                    "resume_skill": "инкапсуляция",
                    "reason": "Элемент парадигмы ООП",
                    "relevance": "Частичная аналогичность",
                },
                {
                    "vacancy_skill": "oop",
                    "resume_skill": "полиморфизм",
                    "relevance": "Частичная аналогичность",
                    "reason": "Элемент парадигмы ООП",
                },
                {
                    "vacancy_skill": "oop",
                    "resume_skill": "абстракция",
                    "relevance": "Частичная аналогичность",
                    "reason": "Элемент парадигмы ООП",
                },
                {
                    "vacancy_skill": "oop",
                    "resume_skill": "Python",
                    "relevance": "Отсутствует аналогичность",
                    "reason": "Кандидат может знать Python, но не факт, что он знает ООП",
                },
                {
                    "vacancy_skill": "oop",
                    "resume_skill": "Django Framework",
                    "relevance": "Отсутствует аналогичность",
                    "reason": "Django — фреймворк для веб-разработки, но не заменяет ООП как парадигму программирования",
                },
                {
                    "vacancy_skill": "oop",
                    "resume_skill": "DRF",
                    "relevance": "Отсутствует аналогичность",
                    "reason": "DRF — библиотека для создания REST API, не заменяет ООП как парадигму",
                },
                {
                    "vacancy_skill": "oop",
                    "resume_skill": "FastAPI",
                    "relevance": "Отсутствует аналогичность",
                    "reason": "FastAPI — фреймворк для создания API, не заменяет ООП как парадигму",
                },
                {
                    "vacancy_skill": "oop",
                    "resume_skill": "PostgreSQL",
                    "relevance": "Отсутствует аналогичность",
                    "reason": "PostgreSQL — СУБД, не связан с ООП",
                },
                {
                    "vacancy_skill": "oop",
                    "resume_skill": "ElasticSearch",
                    "relevance": "Отсутствует аналогичность",
                    "reason": "ElasticSearch — система поиска, не связана с ООП",
                },
                {
                    "vacancy_skill": "oop",
                    "resume_skill": "Celery",
                    "relevance": "Отсутствует аналогичность",
                    "reason": "Celery — инструмент для асинхронных задач, не заменяет ООП как парадигму",
                },
                {
                    "vacancy_skill": "oop",
                    "resume_skill": "Git",
                    "relevance": "Отсутствует аналогичность",
                    "reason": "Git — система контроля версий, не связана с ООП",
                },
                {
                    "vacancy_skill": "oop",
                    "resume_skill": "Nginx",
                    "relevance": "Отсутствует аналогичность",
                    "reason": "Nginx — веб-сервер, не связан с ООП",
                },
                {
                    "vacancy_skill": "oop",
                    "resume_skill": "Linux",
                    "relevance": "Отсутствует аналогичность",
                    "reason": "Linux — операционная система, не связана с ООП",
                },
                {
                    "vacancy_skill": "oop",
                    "resume_skill": "Docker",
                    "relevance": "Отсутствует аналогичность",
                    "reason": "Docker — инструмент контейнеризации, не заменяет ООП как парадигму",
                },
                {
                    "vacancy_skill": "oop",
                    "resume_skill": "k8s",
                    "relevance": "Отсутствует аналогичность",
                    "reason": "k8s — платформа оркестрации контейнеров, не связана с ООП",
                },
                {
                    "vacancy_skill": "oop",
                    "resume_skill": "Gunicorn",
                    "relevance": "Отсутствует аналогичность",
                    "reason": "Gunicorn — WSGI-сервер, не заменяет ООП как парадигму",
                },
                {
                    "vacancy_skill": "oop",
                    "resume_skill": "RabbitMQ",
                    "relevance": "Отсутствует аналогичность",
                    "reason": "RabbitMQ — система очередей сообщений, не связана с ООП",
                },
                {
                    "vacancy_skill": "oop",
                    "resume_skill": "Jenkins",
                    "relevance": "Отсутствует аналогичность",
                    "reason": "Jenkins — система CI/CD, не заменяет ООП как парадигму",
                },
                {
                    "vacancy_skill": "oop",
                    "resume_skill": "Gitlab CI",
                    "relevance": "Отсутствует аналогичность",
                    "reason": "Gitlab CI — система непрерывной интеграции, не связана с ООП",
                },
                {
                    "vacancy_skill": "oop",
                    "resume_skill": "HTML",
                    "relevance": "Отсутствует аналогичность",
                    "reason": "HTML — язык разметки, не связан с ООП",
                },
                {
                    "vacancy_skill": "oop",
                    "resume_skill": "CSS",
                    "relevance": "Отсутствует аналогичность",
                    "reason": "CSS — язык стилей, не связан с ООП",
                },
                {
                    "vacancy_skill": "oop",
                    "resume_skill": "JavaScript",
                    "relevance": "Отсутствует аналогичность",
                    "reason": "Кандидат может знать JavaScript,  но не факт, что он знает ООП",
                },
                {
                    "vacancy_skill": "oop",
                    "resume_skill": "TypeScript",
                    "relevance": "Отсутствует аналогичность",
                    "reason": "Кандидат может знать TypeScript, но не факт, что он знает ООП",
                },
            ]
        },
    }
]

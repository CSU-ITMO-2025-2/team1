human_motivation_block_prompt = """
Ниже переданы входные данные. Сформируйте 10 вопросов, ориентированные на требования вакансии, по «узким местам» мотивации кандидата (по 2 на каждый блок) — career_ambitions, job_search_factors, salary_expectations, company_role, motivation_goals — и верните ТОЛЬКО JSON строго по заданной схеме из system-сообщения (без любого дополнительного текста).

### Вакансия
{vacancy_text}

### Резюме
{resume_text}

### Оценка опыта работы
{work_experience_evaluation}

### Оценка зарплатных ожиданий
{salary_evaluation}
"""

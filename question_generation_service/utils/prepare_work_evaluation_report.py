def format_work_experience_report(report: dict) -> str:
    """
    Форматирует блок work_experience_report в человекочитаемый отчёт.

    Args:
        report (dict): Словарь с данными work_experience_report

    Returns:
        str: Текстовый отчёт
    """
    work_exp_raw_block = report.get("work_experience_report")

    if not work_exp_raw_block:
        return "❌ Данные по опыту работы отсутствуют"

    job_change = work_exp_raw_block["job_change_data"]
    exp_data = work_exp_raw_block["work_exp_data"]

    # Основной блок
    work_experience_evaluation_block = f"""
📊 Отчёт по опыту работы

▪ Итоговый балл: {work_exp_raw_block['final_score']} из {work_exp_raw_block['max_score']}
▪ Требуемый опыт по вакансии: {work_exp_raw_block['required_exp_years']} лет

🔄 Проверка частоты смены работы:
- Результат: {job_change['job_change_reason']}
- Балл: {job_change['job_change_score']} / {job_change['job_change_score_max_score']}
- Период анализа: {job_change['job_change_check_period']}

👔 Опыт работы:
- Общий стаж: {exp_data['total_work_exp']} ({exp_data['total_work_exp_months']} мес.)
- Релевантный опыт: {exp_data['total_relevant_work_exp']} ({exp_data['total_relevant_work_exp_months']} мес.)
- Нерелевантный опыт: {exp_data['total_irrelevant_work_exp']} ({exp_data['total_irrelevant_work_exp_months']} мес.)
- Балл: {exp_data['work_exp_score']} / {exp_data['work_exp_max_score']}
- Комментарий: {exp_data['work_exp_comment']}

🏢 Подробности по релевантному опыту:
"""

    # Перебираем релевантный опыт
    for item in exp_data["relevant_work_exp_list"]:
        work_experience_evaluation_block += f"""
- Компания: {item['company_name']}
  Должность: {item['position']}
  Период: {item['start_date']} – {"настоящее время" if item['currently_working'] else item['end_date']}
  Продолжительность: {item['true_duration_str']}
  Задачи: {item['work_tasks']}
  Причина релевантности: {item['reason']}
"""

    # Если есть нерелевантный опыт
    if exp_data["irrelevant_work_exp_list"]:
        work_experience_evaluation_block += "\n❌ Нерелевантный опыт:\n"
        for item in exp_data["irrelevant_work_exp_list"]:
            work_experience_evaluation_block += (
                f"- {item['company_name']} – {item['position']} ({item['duration']})\n"
            )

    return work_experience_evaluation_block.strip()

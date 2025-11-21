def format_salary_report(report: dict) -> str:
    """
    Форматирует блок salary_report в человекочитаемый отчёт.

    Args:
        report (dict): Словарь, содержащий ключ "salary_report" или "salary_evaluation".

    Returns:
        str: Текстовый отчёт.
    """
    sr = (
        report.get("salary_evaluation")  # иногда ключ может называться так
    )

    if not sr:
        return "❌ Данные по зарплатным ожиданиям отсутствуют"

    score = sr.get("score", 0)
    max_score = sr.get("max_score", 0)
    message = sr.get("message", "-")
    resume_salary = sr.get("resume_salary", "—")
    vacancy_salary = sr.get("vacancy_salary", "—")
    deviation_percent = sr.get("deviation_percent", None)

    header = (
        f"💰 Отчёт по зарплатным ожиданиям\n\n"
        f"▪ Итоговый балл: {score} из {max_score}\n"
    )

    body = f"📌 {message}\n\n"
    body += f"- Зарплата в резюме: {resume_salary}\n"
    body += f"- Зарплата в вакансии: {vacancy_salary}\n"

    if deviation_percent is not None:
        body += f"- Отклонение: {deviation_percent:.1f}%\n"

    return (header + body).strip()

def format_skills_report(report: dict, compact: bool = False) -> str:
    """
    Форматирует блок skills_report в человекочитаемый отчёт.

    Args:
        report (dict): Словарь, содержащий ключ "skills_report" (как в примере).
        compact (bool): Если True — вывод более компактный (в одну строку на блок).

    Returns:
        str: Текстовый отчёт.
    """
    sr = report.get("skills_report")
    if not sr:
        return "❌ Данные по профессиональным навыкам отсутствуют"

    status = sr.get("status", "-")
    max_score = sr.get("max_score", 0)
    score = sr.get("score", 0)

    skills_data = sr.get("skills_data", {})
    must_have = skills_data.get("must_have_skills", {}) or {}
    nice_to_have = skills_data.get("nice_to_have_skills", {}) or {}

    must_stats = sr.get("must_have_stats", {}) or {}
    nice_stats = sr.get("nice_to_have_stats", {}) or {}

    def _fmt_stats(stats: dict) -> str:
        return (
            f"всего: {stats.get('total_skills', 0)}, "
            f"релевантных: {stats.get('relevant_count', 0)} "
            f"(current: {stats.get('current_count', 0)}, half: {stats.get('half_count', 0)}), "
            f"не релевантных: {stats.get('no_relevance_count', 0)}, "
            f"покрытие: {stats.get('relevant_percentage', 0)}%"
        )

    def _fmt_skill_line(skill_name: str, data: dict) -> str:
        rel = data.get("relevance", "-")
        rel_skill = data.get("relevant_skill", "-")
        reason = data.get("reason", "")
        # Короткие маркеры для релевантности
        mark = {"current": "✅", "half": "🟡"}.get(rel, "❌")
        return f"- {mark} {skill_name} — {rel} (совпадение: {rel_skill}){f'. Причина: {reason}' if reason else ''}"

    def _fmt_compact_list(skills: dict) -> str:
        # Превращаем в вид: skill1[current], skill2[half], ...
        items = []
        for k, v in skills.items():
            rel = v.get("relevance", "-")
            tag = {"current": "current", "half": "half"}.get(rel, "no")
            items.append(f"{k}[{tag}]")
        return ", ".join(items) if items else "—"

    header = (
        f"🧩 Отчёт по профессиональным навыкам\n\n"
        f"▪ Статус: {status}\n"
        f"▪ Итоговый балл: {score} из {max_score}\n"
    )

    if compact:
        body = (
            "🔹 Must-have:\n"
            f"- Навыки: { _fmt_compact_list(must_have) }\n"
            f"- Статистика: {_fmt_stats(must_stats)}\n\n"
            "🔸 Nice-to-have:\n"
            f"- Навыки: { _fmt_compact_list(nice_to_have) }\n"
            f"- Статистика: {_fmt_stats(nice_stats)}"
        )
        return (header + body).strip()

    # Подробный режим
    lines = [header]

    lines.append("🔹 Must-have навыки:")
    if must_have:
        for name, data in must_have.items():
            lines.append(_fmt_skill_line(name, data))
    else:
        lines.append("- —")
    lines.append(f"Статистика: {_fmt_stats(must_stats)}\n")

    lines.append("🔸 Nice-to-have навыки:")
    if nice_to_have:
        for name, data in nice_to_have.items():
            lines.append(_fmt_skill_line(name, data))
    else:
        lines.append("- —")
    lines.append(f"Статистика: {_fmt_stats(nice_stats)}")

    return "\n".join(lines).strip()

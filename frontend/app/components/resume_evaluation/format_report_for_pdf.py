"""Форматирование отчета по оценке резюме для экспорта в PDF."""


def format_resume_report_for_pdf(result: dict) -> str:
    """Форматирует результат оценки резюме в текстовый вид для PDF.

    Args:
        result: Словарь с результатами оценки резюме

    Returns:
        Отформатированная строка с отчетом в markdown формате

    """
    lines = []

    # --- Общие баллы ---
    salary_score = result.get("salary_evaluation", {}).get("score", 0)
    edu_score = result.get("education_evaluation", {}).get("final_score", 0)
    schedule_score = result.get("additional_evaluation", {}).get("score", 0)
    work_exp_score = result.get("work_experience_report", {}).get("final_score", 0)
    skills_score = result.get("skills_report", {}).get("score", 0)

    salary_max = 5
    edu_max = 20
    schedule_max = 5
    work_max = result.get("work_experience_report", {}).get("max_score", 0)
    skills_max = result.get("skills_report", {}).get("max_score", 0)

    total_score = salary_score + edu_score + schedule_score + work_exp_score + skills_score
    total_max = salary_max + edu_max + schedule_max + work_max + skills_max
    percentage = round(total_score / total_max * 100, 1) if total_max else 0

    lines.append(f"**Общая оценка:** {total_score} / {total_max} ({percentage}%)")
    lines.append("")
    lines.append(f"**Рекомендация:** {'Рекомендован' if percentage > 70 else 'Не рекомендован'}")
    lines.append("")
    lines.append("")

    # --- Баллы по блокам ---
    lines.append("**Сводка по блокам**")
    lines.append("")

    salary_pct = round(salary_score / salary_max * 100, 1) if salary_max else 0
    edu_pct = round(edu_score / edu_max * 100, 1) if edu_max else 0
    schedule_pct = round(schedule_score / schedule_max * 100, 1) if schedule_max else 0
    work_exp_pct = round(work_exp_score / work_max * 100, 1) if work_max else 0
    skills_pct = round(skills_score / skills_max * 100, 1) if skills_max else 0

    lines.append(f"- Навыки: {skills_score} / {skills_max} ({skills_pct}%)")
    lines.append(f"- Опыт работы: {work_exp_score} / {work_max} ({work_exp_pct}%)")
    lines.append(f"- Образование: {edu_score} / {edu_max} ({edu_pct}%)")
    lines.append(f"- Зарплата: {salary_score} / {salary_max} ({salary_pct}%)")
    lines.append(f"- График/условия: {schedule_score} / {schedule_max} ({schedule_pct}%)")
    lines.append("")
    lines.append("")

    # --- НАВЫКИ ---
    lines.append("**1. Навыки**")
    lines.append("")
    lines.append(f"**Баллы:** {skills_score} / {skills_max}")
    lines.append("")

    sr = result.get("skills_report", {})
    skills_data = sr.get("skills_data", {})
    must_map = skills_data.get("must_have_skills", {})
    nice_map = skills_data.get("nice_to_have_skills", {})
    must_stats = sr.get("must_have_stats", {})
    nice_stats = sr.get("nice_to_have_stats", {})

    # Обязательные навыки
    lines.append("**Обязательные навыки:**")
    lines.append("")
    if must_stats:
        total = must_stats.get("total_skills", 0)
        rel_cnt = must_stats.get("relevant_count", 0)
        rel_pct = must_stats.get("relevant_percentage", 0)
        lines.append(f"Совпадений: {rel_cnt} из {total} ({rel_pct}%)")
        lines.append("")

    if must_map:
        for vac_skill, meta in must_map.items():
            rel = meta.get("relevance", "no_relevance")
            rs = meta.get("relevant_skill")
            reason = meta.get("reason")

            if rel == "current":
                status = "✓ Полное совпадение"
            elif rel == "half":
                status = "~ Частичное совпадение"
            else:
                status = "✗ Нет совпадения"

            lines.append(f"- **{vac_skill}** → {rs if rs else '—'}")
            lines.append(f"  {status}")
            if reason and rel in ("half", "no_relevance"):
                lines.append(f"  Причина: {reason}")
        lines.append("")
    else:
        lines.append("Нет данных")
        lines.append("")

    # Желательные навыки
    lines.append("**Желательные навыки:**")
    lines.append("")
    if nice_stats:
        total = nice_stats.get("total_skills", 0)
        rel_cnt = nice_stats.get("relevant_count", 0)
        rel_pct = nice_stats.get("relevant_percentage", 0)
        lines.append(f"Совпадений: {rel_cnt} из {total} ({rel_pct}%)")
        lines.append("")

    if nice_map:
        for vac_skill, meta in nice_map.items():
            rel = meta.get("relevance", "no_relevance")
            rs = meta.get("relevant_skill")

            if rel == "current":
                status = "✓"
            elif rel == "half":
                status = "~"
            else:
                status = "✗"

            lines.append(f"- **{vac_skill}** → {rs if rs else '—'} ({status})")
        lines.append("")
    else:
        lines.append("Нет данных")
        lines.append("")

    lines.append("")

    # --- ОПЫТ РАБОТЫ ---
    lines.append("**2. Опыт работы**")
    lines.append("")

    we = result.get("work_experience_report", {})
    lines.append(f"**Баллы:** {work_exp_score} / {work_max}")
    lines.append("")
    
    we_data = we.get("work_exp_data", {})
    req_years = we.get("required_exp_years", 0) or 0

    tot_m = int(we_data.get("total_work_exp_months", 0) or 0)
    tot_rel_m = int(we_data.get("total_relevant_work_exp_months", 0) or 0)
    tot_irrel_m = int(we_data.get("total_irrelevant_work_exp_months", 0) or 0)

    def months_to_str(m: int) -> str:
        y, mm = divmod(int(m), 12)
        return f"{y} г. {mm} мес."

    lines.append(f"Суммарный опыт: {months_to_str(tot_m)}")
    lines.append(f"Релевантный опыт: {months_to_str(tot_rel_m)}")
    lines.append(f"Нерелевантный опыт: {months_to_str(tot_irrel_m)}")
    lines.append(f"Требуемый опыт: {months_to_str(int(req_years * 12))}")
    lines.append("")

    comment = we_data.get("work_exp_comment")
    if comment:
        lines.append(f"Комментарий: {comment}")
        lines.append("")

    # Релевантный опыт
    rel_list = we_data.get("relevant_work_exp_list", []) or []
    if rel_list:
        lines.append("**Релевантный опыт:**")
        lines.append("")
        for i, it in enumerate(rel_list, 1):
            lines.append(f"{i}. **{it.get('company_name', '—')}** — {it.get('position', '—')}")
            start = it.get("start_date", "—")
            end = it.get("end_date", "—")
            lines.append(f"   Период: {start} — {end}")
            dur_months = it.get("calculated_duration_months", 0) or 0
            lines.append(f"   Длительность: {months_to_str(dur_months)}")
            if it.get("reason"):
                lines.append(f"   Релевантность: {it['reason']}")
            lines.append("")

    # Смена работы
    jobchg = we.get("job_change_data", {}) or {}
    jc_flag = bool(jobchg.get("job_change_flag"))
    lines.append("**Стабильность:**")
    lines.append("")
    lines.append(f"Частая смена работы: {'Да' if jc_flag else 'Нет'}")
    if jobchg.get("job_change_reason"):
        lines.append(f"Причина: {jobchg['job_change_reason']}")
    lines.append("")
    lines.append("")

    # --- ОБРАЗОВАНИЕ ---
    lines.append("**3. Образование**")
    lines.append("")
    lines.append(f"**Баллы:** {edu_score} / {edu_max}")
    lines.append("")

    edu = result.get("education_evaluation", {}) or {}
    lvl = edu.get("education_level", {}) or {}
    spec = edu.get("education_specialization", {}) or {}
    crs = edu.get("education_courses", {}) or {}

    # Уровень образования
    lines.append("**Уровень образования:**")
    lines.append("")
    req_level = lvl.get("required_vacancy_level") or "Не указано"
    cand_levels = lvl.get("candidate_levels", []) or []
    ok_level = bool(lvl.get("candidate_has_required_level", False)) or (req_level == "Не указано")

    lines.append(f"Требуемый уровень: {req_level}")
    lines.append(f"У кандидата: {', '.join(cand_levels) if cand_levels else '—'}")
    lines.append(f"Соответствие: {'Да' if ok_level else 'Нет'}")

    lvl_score = int(lvl.get("education_level_score", 0) or 0)
    lvl_max = int(lvl.get("max_score", 0) or 0)
    lines.append(f"Баллы: {lvl_score} / {lvl_max}")

    if lvl.get("education_level_comment"):
        lines.append(f"Комментарий: {lvl['education_level_comment']}")
    lines.append("")

    # Специализация
    lines.append("**Специализация:**")
    lines.append("")
    req_specs = [s for s in (spec.get("required_specializations") or []) if s] or ["Не указано"]
    cand_specs = spec.get("candidate_specializations", []) or []

    if "Не указано" in req_specs:
        ok_spec = True
    else:
        chrs = spec.get("candidate_has_required_specialization")
        if isinstance(chrs, list):
            ok_spec = len(chrs) > 0
        else:
            ok_spec = bool(chrs)

    lines.append(f"Требуемая специализация: {', '.join(req_specs)}")
    lines.append(f"У кандидата: {', '.join(cand_specs) if cand_specs else '—'}")
    lines.append(f"Соответствие: {'Да' if ok_spec else 'Нет'}")

    spec_score = int(spec.get("education_specialization_score", 0) or 0)
    spec_max = int(spec.get("max_score", 0) or 0)
    lines.append(f"Баллы: {spec_score} / {spec_max}")

    if spec.get("education_specialization_comment"):
        lines.append(f"Комментарий: {spec['education_specialization_comment']}")
    lines.append("")

    # Курсы
    lines.append("**Курсы:**")
    lines.append("")
    rel_courses = crs.get("relevant_courses", []) or []
    irrel_courses = crs.get("irrelevant_courses", []) or []

    lines.append(f"Релевантных курсов: {len(rel_courses)}")
    lines.append(f"Нерелевантных курсов: {len(irrel_courses)}")
    lines.append("")

    if rel_courses:
        lines.append("**Релевантные курсы:**")
        for i, c in enumerate(rel_courses, 1):
            title = c.get("course_name", "Курс")
            lines.append(f"{i}. {title}")
            if c.get("reason"):
                lines.append(f"   Релевантность: {c['reason']}")
        lines.append("")

    crs_score = int(crs.get("education_courses_score", 0) or 0)
    crs_max = int(crs.get("max_score", 0) or 0)
    lines.append(f"Баллы: {crs_score} / {crs_max}")
    lines.append("")
    lines.append("")

    # --- ЗАРПЛАТА ---
    lines.append("**4. Зарплатные ожидания**")
    lines.append("")
    lines.append(f"**Баллы:** {salary_score} / {salary_max}")
    lines.append("")

    sal = result.get("salary_evaluation", {})
    lines.append(f"Зарплата в вакансии: {sal.get('vacancy_salary', '—')}")
    lines.append(f"Зарплата в резюме: {sal.get('resume_salary', '—')}")
    lines.append(f"Разница: {sal.get('deviation_percent', 0)}%")
    lines.append(f"Комментарий: {sal.get('message', '—')}")
    lines.append("")
    lines.append("")

    # --- ГРАФИК И УСЛОВИЯ ---
    lines.append("**5. График и условия**")
    lines.append("")

    add_eval = result.get("additional_evaluation", {})
    match = add_eval.get("match", False)
    sched_score = add_eval.get("score", 0)
    
    lines.append(f"**Баллы:** {sched_score} / {schedule_max}")
    lines.append("")

    vac_sched = add_eval.get("vacancy_schedule", {})
    vac_list = vac_sched.get("schedule", []) or []
    res_sched = add_eval.get("resume_schedule", {})
    res_list = res_sched.get("schedule", []) or []

    lines.append("График в вакансии:")
    if vac_list:
        for s in vac_list:
            lines.append(f"  - {s}")
    else:
        lines.append("  Не указан")
    lines.append("")

    lines.append("График в резюме:")
    if res_list:
        for s in res_list:
            lines.append(f"  - {s}")
    else:
        lines.append("  Не указан")
    lines.append("")

    lines.append(f"Совпадение: {'Да' if match else 'Нет'}")

    if add_eval.get("reason"):
        lines.append(f"Комментарий: {add_eval['reason']}")

    return "\n".join(lines)


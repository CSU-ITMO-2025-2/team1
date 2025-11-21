import plotly.graph_objects as go
import streamlit as st


def _donut(
    score: float,
    max_score: float,
    color: str | None = None,
    size: int = 60,
    key: str = None,
):
    """Мини-колечко без тулбаров, прижатое к левому краю."""
    ratio = 0 if max_score == 0 else float(score) / float(max_score)
    if color is None:
        if ratio <= 0.5:
            color = "#ff6666"
        elif ratio < 0.75:
            color = "#ffcc66"
        else:
            color = "#66cc66"

    fig = go.Figure(
        data=[
            go.Pie(
                values=[ratio, 1 - ratio],
                hole=0.7,
                marker_colors=[color, "#e6e6e6"],
                sort=False,
                direction="clockwise",
                textinfo="none",
            ),
        ],
    )
    fig.add_annotation(
        x=0.5,
        y=0.5,
        text=f"{score} / {max_score}",
        font_size=15,
        showarrow=False,
    )
    # Увеличиваем размер графика для предотвращения обрезки
    # Добавляем 40px запаса (20% от базового размера 60-100px)
    chart_size = size + 40
    fig.update_layout(
        showlegend=False,
        margin=dict(t=15, b=15, l=15, r=15),
        height=chart_size,
        width=chart_size,
        autosize=False,
    )

    # добавляем key для уникальности
    st.plotly_chart(
        fig,
        width="content",
        config={"displayModeBar": False},
        key=key,
    )


def get_report(result: dict):
    # --- собираем оценки ---
    salary_score = result["salary_evaluation"].get("score", 0)
    salary_max = 5

    edu_score = result["education_evaluation"].get("final_score", 0)
    edu_max = 20

    schedule_score = result["additional_evaluation"].get("score", 0)
    schedule_max = 5

    we = result["work_experience_report"] or {}
    work_exp_score = we.get("final_score", 0)
    work_exp_max = we.get("max_score", 0)

    sr = result["skills_report"] or {}
    skills_score = sr.get("score", 0)
    skills_max = sr.get("max_score", 0)

    # --- суммируем ---
    total_score = salary_score + edu_score + schedule_score + work_exp_score + skills_score
    total_max = salary_max + edu_max + schedule_max + work_exp_max + skills_max
    percentage = round(total_score / total_max * 100, 1) if total_max else 0

    st.markdown("### Отчет по резюме")
    col_vals, col_chart = st.columns([2, 1], vertical_alignment="top")

    with col_vals:
        st.write("**Баллы по блокам:**")

        salary_pct = round(salary_score / salary_max * 100, 1) if salary_max else 0
        edu_pct = round(edu_score / edu_max * 100, 1) if edu_max else 0
        schedule_pct = round(schedule_score / schedule_max * 100, 1) if schedule_max else 0
        work_exp_pct = round(work_exp_score / work_exp_max * 100, 1) if work_exp_max else 0
        skills_pct = round(skills_score / skills_max * 100, 1) if skills_max else 0

        st.write(f"- Навыки: {skills_score} / {skills_max} ({skills_pct}%)")
        st.write(f"- Опыт работы: {work_exp_score} / {work_exp_max} ({work_exp_pct}%)")
        st.write(f"- Образование: {edu_score} / {edu_max} ({edu_pct}%)")
        st.write(f"- Зарплата: {salary_score} / {salary_max} ({salary_pct}%)")
        st.write(f"- График/условия: {schedule_score} / {schedule_max} ({schedule_pct}%)")

    with col_chart:
        _donut(round(percentage), 100, size=100, key="total_donut")

        st.write(" ")
        st.markdown(" ")
        st.write(" ")
        st.markdown(" ")
        st.badge(f"**Итог: {percentage}%**")

        # Рекомендация
        recommended = "Да" if percentage > 70 else "Нет"
        rec_color = "#66cc66" if percentage > 70 else "#ff6666"
        st.markdown(f"**Рекомендован:** <span style='color:{rec_color}'>{recommended}</span>", unsafe_allow_html=True)

    st.divider()

    # ---------- 🛠 Навыки ----------
    # ==== ВХОДНЫЕ ДАННЫЕ ====
    skills_data = sr.get("skills_data", {})
    must_map = skills_data.get("must_have_skills", {})  # dict: vacancy_skill -> {relevance, relevant_skill, reason}
    nice_map = skills_data.get("nice_to_have_skills", {})

    must_stats = sr.get("must_have_stats", {})  # {total_skills, relevant_count, relevant_percentage, ...}
    nice_stats = sr.get("nice_to_have_stats", {})

    # ---- утилита бейджа с graceful fallback ----
    def _badge(text: str, color: str = "gray"):
        """Пытаемся использовать st.badge (Streamlit 1.3x+).
        Если нет — рисуем простой HTML-бейдж.
        Доступные цвета для fallback: green/yellow/red/gray.
        """
        try:
            # у свежих версий: st.badge(text, color="green"/"red"/"orange"/"blue"/"violet"/"gray")
            st.badge(text, color=color)
        except Exception:
            bg = {"green": "#E6F4EA", "yellow": "#FFF6D6", "red": "#FDE8E8", "gray": "#EEE"}[color]
            fg = {"green": "#137333", "yellow": "#7A5C00", "red": "#B91C1C", "gray": "#444"}[color]
            st.markdown(
                f"<span style='display:inline-block;padding:4px 10px;border-radius:999px;"
                f"background:{bg};color:{fg};font-weight:600;font-size:12px;'>{text}</span>",
                unsafe_allow_html=True,
            )

    def _relevance_color(rel: str) -> str:
        # current -> зелёный, half -> жёлтый, no_relevance -> красный
        return {"current": "green", "half": "orange", "no_relevance": "red"}.get(rel, "gray")

    def _render_skill_line(vacancy_skill: str, meta: dict):
        rel = (meta or {}).get("relevance", "no_relevance")
        rs = (meta or {}).get("relevant_skill")
        reason = (meta or {}).get("reason")

        col_l, col_r = st.columns([3, 2])
        with col_l:
            # Вакансия → Резюме (или "—")
            right = rs if rs else "—"
            st.write(f"**{vacancy_skill}** → {right}")
        with col_r:
            _badge(
                {"current": "✅ Совпадение", "half": "🟡 Частично", "no_relevance": "❌ Нет совпадения"}.get(rel, "—"),
                color=_relevance_color(rel),
            )
        # Пояснение для half / no_relevance (и при желании для current)
        if rel in ("half", "no_relevance") and reason:
            st.caption(reason)

    def _render_block(title: str, mapping: dict, stats: dict, key: str):
        with st.container(border=True):
            top_l, top_r = st.columns([3, 2], vertical_alignment="center")
            with top_l:
                st.markdown(f"**{title}**")
                total = stats.get("total_skills", len(mapping))
                rel_pct = stats.get("relevant_percentage")
                rel_cnt = stats.get("relevant_count")
                if rel_pct is None:
                    # если статистика не пришла — посчитаем по current/half
                    rel_cnt = sum(1 for v in mapping.values() if (v or {}).get("relevance") in ("current", "half"))
                    total = len(mapping) or 1
                    rel_pct = round(rel_cnt / total * 100, 1)
                st.caption(f"Совпало: {rel_cnt} из {total}  •  {rel_pct}%")

            with top_r:
                # Небольшой прогресс по блоку
                st.progress((rel_pct or 0) / 100)

            st.markdown("---")

            if mapping:
                for vac_skill, meta in mapping.items():
                    _render_skill_line(vac_skill, meta)
            else:
                st.write("—")

    # ====== РЕНДЕР БЛОКА «НАВЫКИ» ======
    st.markdown("#### 🛠 Навыки")
    sk_left, space, sk_right = st.columns([1.6, 0.05, 1], vertical_alignment="top")

    with sk_left:
        _render_block("Обязательные навыки", must_map, must_stats, key="must")
        st.markdown("")
        _render_block("Желательные навыки", nice_map, nice_stats, key="nice")

    with sk_right:
        # общий донат и цифры по навыкам
        _donut(skills_score, skills_max, size=85, key="skills_donut")
        st.write(f"**Оценка:** {skills_score} / {skills_max}")

        st.markdown("---")
        # Подробная сводка по must-have
        if must_stats:
            st.markdown("**📌 Обязательные навыки для вакансии**")
            st.write(f"- Всего навыков в вакансии: {must_stats.get('total_skills', 0)}")
            st.write(f"- Совпадений с резюме: {must_stats.get('relevant_count', 0)}")
            st.write(f"- - Полных совпадений: {must_stats.get('current_count', 0)}")
            st.write(f"- - Частичных совпадений: {must_stats.get('half_count', 0)}")
            st.write(f"- - Без совпадений: {must_stats.get('no_relevance_count', 0)}")
            st.write(f"- Процент совпадений: {must_stats.get('relevant_percentage', 0)}%")

        st.markdown("---")

        # Подробная сводка по nice-to-have
        if nice_stats:
            st.markdown("**📌 Желательные навыки для вакансии**")
            st.write(f"- Всего навыков в вакансии: {nice_stats.get('total_skills', 0)}")
            st.write(f"- Совпадений с резюме: {nice_stats.get('relevant_count', 0)}")
            st.write(f"- - Полных совпадений: {nice_stats.get('current_count', 0)}")
            st.write(f"- - Частичных совпадений: {nice_stats.get('half_count', 0)}")
            st.write(f"- - Без совпадений: {nice_stats.get('no_relevance_count', 0)}")
            st.write(f"- Процент совпадений: {nice_stats.get('relevant_percentage', 0)}%")

    st.divider()

    # ---------- 🧭 Опыт работы ----------
    wer = we
    max_score = wer.get("max_score", 35)
    final_score = wer.get("final_score", 0)

    jobchg = wer.get("job_change_data", {}) or {}
    we_data = wer.get("work_exp_data", {}) or {}

    # Требуемый опыт
    req_years = wer.get("required_exp_years", 0) or 0
    req_months_total = int(req_years * 12)

    # Фактический суммарный опыт
    tot_m = int(we_data.get("total_work_exp_months", 0) or 0)
    tot_rel_m = int(we_data.get("total_relevant_work_exp_months", 0) or 0)
    tot_irrel_m = int(we_data.get("total_irrelevant_work_exp_months", 0) or 0)

    rel_list = we_data.get("relevant_work_exp_list", []) or []
    irrel_list = we_data.get("irrelevant_work_exp_list", []) or []

    def _months_to_str(m: int) -> str:
        y, mm = divmod(int(m), 12)
        return f"{y} г. {mm} мес."

    def _safe_dt(v):
        import datetime as _dt

        if isinstance(v, _dt.date):
            return v.strftime("%Y-%m-%d")
        return v if v is not None else "н.в."

    st.markdown("#### 🧭 Опыт работы")

    hdr_l, hdr_r = st.columns([1, 1], vertical_alignment="center")
    with hdr_l:
        st.write(f"**Суммарный опыт:** {_months_to_str(tot_m)}")
        st.write(f"**Релевантный опыт:** {_months_to_str(tot_rel_m)}")
        st.write(f"**Нерелевантный опыт:** {_months_to_str(tot_irrel_m)}")
        st.write(f"**Требуемый опыт:** {_months_to_str(req_months_total)}")

        cover_pct = round((tot_rel_m / req_months_total * 100), 1) if req_months_total else 0
        st.caption(f"Покрытие требований релевантным опытом: {cover_pct}%")

    with hdr_r:
        _donut(final_score, max_score, size=80, key="experience_donut_total")
        st.write(f"**Итог по блоку:** {final_score} / {max_score}")

    st.markdown("---")

    # --- Подсекция: ⚙️ Соответствие требованиям по опыту
    st.markdown("##### ⚙️ Опыт по требованиям")

    comment = we_data.get("work_exp_comment")
    if comment:
        st.info(comment)

    # 🔶 Предупреждение, если в какой-то записи нельзя определить длительность
    def _has_missing_duration(records: list[dict]) -> bool:
        for it in records or []:
            # считаем «пропуском», если has_duration=False ИЛИ нет duration и нет рассчитанной длительности
            if not it.get("has_duration", True) or (
                not it.get("duration") and not it.get("calculated_duration_months")
            ):
                return True
        return False

    if _has_missing_duration(rel_list) or _has_missing_duration(irrel_list):
        st.warning(
            "По одной из прошлых работ кандидата невозможно определить длительность. "
            "Возможно, реальный опыт кандидата больше.",
        )

    with st.expander("Релевантный опыт (по местам работы)", expanded=True):
        if rel_list:
            for i, it in enumerate(rel_list, 1):
                with st.container(border=True):
                    top_l, top_r = st.columns([3, 2])
                    with top_l:
                        st.markdown(f"**{i}. {it.get('company_name', '—')}** — {it.get('position', '—')}")
                        st.write(f"Период: {_safe_dt(it.get('start_date'))} — {_safe_dt(it.get('end_date'))}")
                        dur_calc = it.get("calculated_duration_str") or _months_to_str(
                            it.get("calculated_duration_months", 0) or 0,
                        )
                        st.write(f"Длительность (по расчёту): {dur_calc}")
                        if it.get("work_tasks"):
                            st.caption(it.get("work_tasks"))
                    with top_r:
                        if it.get("reason"):
                            st.write(f"**Почему релевантно:** {it['reason']}")
        else:
            st.write("Нет релевантных записей.")

    with st.expander("Нерелевантный опыт"):
        if irrel_list:
            for j, it in enumerate(irrel_list, 1):
                with st.container(border=True):
                    st.markdown(f"**{j}. {it.get('company_name', '—')}** — {it.get('position', '—')}")
                    st.write(f"Период: {_safe_dt(it.get('start_date'))} — {_safe_dt(it.get('end_date'))}")
        else:
            st.write("Нет нерелевантных записей.")

    st.markdown("---")

    # --- Подсекция: 🔁 Стабильность / смены работы
    st.markdown("##### 🔁 Стабильность и смены работы")

    jc_flag = bool(jobchg.get("job_change_flag"))
    period = jobchg.get("job_change_check_period", "—")

    st.write(f"**Частая смена работы:** {'Да' if jc_flag else 'Нет'}")
    st.caption(f"Период проверки: {period}")

    if jobchg.get("job_change_reason"):
        st.info(jobchg["job_change_reason"])

    st.divider()

    # ---------- 🎓 Образование  ----------
    edu = result.get("education_evaluation", {}) or {}

    lvl = edu.get("education_level", {}) or {}
    spec = edu.get("education_specialization", {}) or {}
    crs = edu.get("education_courses", {}) or {}

    final_score = int(edu.get("final_score", 0) or 0)
    max_possible = int(lvl.get("max_score", 0)) + int(spec.get("max_score", 0)) + int(crs.get("max_score", 0))
    if not max_possible:
        # резервная логика на случай, если max_score в подблоках отсутствуют
        max_possible = 20

    # fallback для _badge, если выше не определён
    if "_badge" not in globals():

        def _badge(text: str, color: str = "gray"):
            try:
                st.badge(text, color=color)
            except Exception:
                bg = {
                    "green": "#E6F4EA",
                    "orange": "#FFF2CC",
                    "red": "#FDE8E8",
                    "blue": "#E8F0FE",
                    "violet": "#F3E8FF",
                    "gray": "#EEE",
                }.get(color, "#EEE")
                fg = {
                    "green": "#137333",
                    "orange": "#7A5C00",
                    "red": "#B91C1C",
                    "blue": "#174EA6",
                    "violet": "#6B21A8",
                    "gray": "#444",
                }.get(color, "#444")
                st.markdown(
                    f"<span style='display:inline-block;padding:4px 10px;border-radius:999px;"
                    f"background:{bg};color:{fg};font-weight:600;font-size:12px;'>{text}</span>",
                    unsafe_allow_html=True,
                )

    st.markdown("#### 🎓 Образование")
    e_left, e_right = st.columns([1.6, 1], vertical_alignment="top")

    with e_left:
        # ====== Уровень образования ======
        with st.container(border=True):
            st.markdown("**Уровень образования**")
            req_level = lvl.get("required_vacancy_level") or "Не указано"
            st.write(f"- Требуемый уровень (вакансия): {req_level}")
            cand_levels = lvl.get("candidate_levels", []) or []
            st.write(f"- У кандидата: {', '.join(cand_levels) if cand_levels else '—'}")

            ok_level = bool(lvl.get("candidate_has_required_level", False)) or (req_level == "Не указано")
            _badge("Соответствует" if ok_level else "Не соответствует", color="green" if ok_level else "red")

            lvl_score = int(lvl.get("education_level_score", 0) or 0)
            lvl_max = int(lvl.get("max_score", 0) or 0)
            st.caption(f"Баллы: {lvl_score} / {lvl_max}")
            if lvl.get("education_level_comment"):
                st.info(lvl["education_level_comment"])

        # ====== Специализация ======
        with st.container(border=True):
            st.markdown("**Специализация**")
            req_specs = [s for s in (spec.get("required_specializations") or []) if s] or ["Не указано"]
            cand_specs = spec.get("candidate_specializations", []) or []

            st.write(f"- Требуемая специализация (вакансия): {', '.join(req_specs)}")
            st.write(f"- У кандидата: {', '.join(cand_specs) if cand_specs else '—'}")

            # если в вакансии "Не указано" — считаем, что ок
            if "Не указано" in req_specs:
                ok_spec = True
            else:
                # candidate_has_required_specialization может быть списком совпавших спецов
                chrs = spec.get("candidate_has_required_specialization")
                if isinstance(chrs, list):
                    ok_spec = len(chrs) > 0
                else:
                    ok_spec = bool(chrs)

            _badge("Соответствует" if ok_spec else "Не соответствует", color="green" if ok_spec else "red")

            spec_score = int(spec.get("education_specialization_score", 0) or 0)
            spec_max = int(spec.get("max_score", 0) or 0)
            st.caption(f"Баллы: {spec_score} / {spec_max}")
            if spec.get("education_specialization_comment"):
                st.info(spec["education_specialization_comment"])

        # ====== Курсы ======
        with st.container(border=True):
            st.markdown("**Курсы**")

            rel_courses = crs.get("relevant_courses", []) or []
            irrel_courses = crs.get("irrelevant_courses", []) or []

            st.write(f"- Релевантных курсов: {len(rel_courses)}")
            if rel_courses:
                with st.expander("Показать релевантные курсы", expanded=True):
                    for i, c in enumerate(rel_courses, 1):
                        with st.container(border=True):
                            title = c.get("course_name", "Курс")
                            st.markdown(f"**{i}. {title}**")
                            if c.get("reason"):
                                st.caption(c["reason"])

            if irrel_courses:
                with st.expander("Нерелевантные курсы", expanded=False):
                    for i, c in enumerate(irrel_courses, 1):
                        st.write(f"{i}. {c.get('course_name', 'Курс')}")

            crs_score = int(crs.get("education_courses_score", 0) or 0)
            crs_max = int(crs.get("max_score", 0) or 0)
            st.caption(f"Баллы: {crs_score} / {crs_max}")
            if crs.get("education_courses_comment"):
                st.info(crs["education_courses_comment"])

    with e_right:
        _donut(final_score, max_possible, size=80, key="education_donut")
        st.write(f"**Итог по образованию:** {final_score} / {max_possible}")

        # Мелкая сводка по подпунктам с «прогрессом»
        st.markdown("---")
        st.markdown("**Сводка по подпунктам**")
        st.write(f"Уровень: {lvl.get('education_level_score', 0)} / {lvl.get('max_score', 10)}")
        st.progress(min((lvl.get("education_level_score", 0) or 0) / (lvl.get("max_score", 10) or 1), 1.0))

        st.write(f"Специализация: {spec.get('education_specialization_score', 0)} / {spec.get('max_score', 5)}")
        st.progress(min((spec.get("education_specialization_score", 0) or 0) / (spec.get("max_score", 5) or 1), 1.0))

        st.write(f"Курсы: {crs.get('education_courses_score', 0)} / {crs.get('max_score', 5)}")
        st.progress(min((crs.get("education_courses_score", 0) or 0) / (crs.get("max_score", 5) or 1), 1.0))

    st.divider()

    # ---------- 💰 Зарплатные ожидания ----------
    salary_eval = result["salary_evaluation"]
    s_score = salary_eval["score"]
    s_max = 5

    if s_score <= 2:
        s_color = "#ff6666"
    elif s_score == 3:
        s_color = "#ffcc66"
    else:
        s_color = "#66cc66"

    st.markdown("#### 💰 Зарплатные ожидания")
    col1, col2 = st.columns([1, 1], vertical_alignment="top")

    with col2:
        _donut(s_score, s_max, color=s_color, size=70, key="salary_donut")
        st.write(f"**Комментарий:** {salary_eval['message']}")

    with col1:
        st.write(f"**Оценка:** {s_score} баллов")
        st.write(f"**Зарплата в вакансии:** {salary_eval['vacancy_salary']}")
        st.write(f"**Зарплата в резюме:** {salary_eval['resume_salary']}")
        st.write(f"**Разница в зарплатах:** {salary_eval['deviation_percent']}%")

    st.divider()

    # ---------- 🕒 График и условия ----------
    add_eval = result.get("additional_evaluation", {})
    match = add_eval.get("match", False)
    score = add_eval.get("score", 0)
    max_score = 5

    st.markdown("#### 🕒 График и условия")
    a_left, a_right = st.columns([1, 1], vertical_alignment="top")

    with a_left:
        st.markdown("**График в вакансии**")
        vac_sched = add_eval.get("vacancy_schedule", {})
        vac_list = vac_sched.get("schedule", []) or []
        if vac_list:
            for s in vac_list:
                st.write(f"• {s}")
        else:
            st.write("• Не указан")

        if vac_sched.get("details"):
            st.write(f"**Комментарий:** {vac_sched['details']}")

        st.markdown("---")

        st.markdown("**График в резюме**")
        res_sched = add_eval.get("resume_schedule", {})
        res_list = res_sched.get("schedule", []) or []
        if res_list:
            for s in res_list:
                st.write(f"• {s}")
        else:
            st.write("• Не указан")

        if res_sched.get("details"):
            st.write(f"**Комментарий:** {res_sched['details']}")

    with a_right:
        _donut(score, max_score, size=70, key="schedule_donut")
        if add_eval.get("reason"):
            st.write(f"**Комментарий:** {add_eval['reason']}")

        st.markdown("---")
        st.write(f"**Совпадение:** {'Да' if match else 'Нет'}")

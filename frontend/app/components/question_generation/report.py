import streamlit as st

def get_report(result: dict):
    # Названия блоков/секций
    BLOCK_META = {
        "experience": {"emoji": "🧰", "title": "Опыт и практики"},
        "motivation": {"emoji": "🎯", "title": "Мотивация"},
        "personal":   {"emoji": "🧠", "title": "Личностные аспекты"},
    }

    SECTION_TITLES = {
        "professional_skills": "Профессиональные навыки",
        "practical_examples":  "Практические кейсы",
        "past_situations":     "Прошлые ситуации",
        "career_goals":        "Карьерные цели",
        "career_ambitions":    "Карьерные амбиции",
        "job_search_factors":  "Факторы выбора работы",
        "salary_expectations": "Зарплатные ожидания",
        "company_role":        "Роль в компании",
        "motivation_goals":    "Цели/драйверы",
        "past_qualities":      "Проявленные качества",
        "soft_skills":         "Софт-скиллы",
        "development_vision":  "Видение развития",
    }

    def _iter_questions(section_dict: dict):
        """Итератор по вопросам q_1, q_2, ..."""
        for key, val in section_dict.items():
            if key.startswith("q_") and isinstance(val, dict):
                yield val.get("question", ""), val.get("details", "")

    # ---------- Рендер ----------
    st.header("🗂️ Вопросы для интервью")

    # какие блоки есть
    available_blocks = [
        k for k in ["experience", "motivation", "personal"]
        if isinstance(result.get(k), dict)
    ]
    if not available_blocks:
        st.info("Нет данных для отображения.")
        return

    # подписи вкладок с количеством вопросов
    tab_labels = []
    for bk in available_blocks:
        block = result[bk]
        q_count = 0
        for s_name, s_dict in block.items():
            if s_name == "status" or not isinstance(s_dict, dict):
                continue
            q_count += sum(1 for _ in _iter_questions(s_dict))
        meta = BLOCK_META.get(bk, {"emoji": "", "title": bk})
        tab_labels.append(f"{meta['emoji']} {meta['title']} ({q_count})")

    tabs = st.tabs(tab_labels)

    for tab, bk in zip(tabs, available_blocks):
        with tab:
            block = result[bk]
            meta = BLOCK_META.get(bk, {"emoji": "", "title": bk})

            st.subheader(f"{meta['emoji']} {meta['title']}")
            st.caption("Откройте нужные разделы и используйте вопросы прямо в интервью.")

            # Секции
            for s_name, s_dict in block.items():
                if s_name == "status" or not isinstance(s_dict, dict):
                    continue

                with st.expander(SECTION_TITLES.get(s_name, s_name), expanded=True):
                    # Список вопросов
                    idx = 1
                    had_questions = False
                    for q_text, details in _iter_questions(s_dict):
                        had_questions = True
                        st.markdown(f"**{idx}. {q_text}**")
                        if details:
                            st.caption(details)
                        idx += 1
                    if not had_questions:
                        st.info("В этом разделе вопросов нет.")
                st.divider()

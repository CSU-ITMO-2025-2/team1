import streamlit as st

# Базовая конфигурация
st.set_page_config(page_title="HR-Assistant", page_icon="🏠", layout="wide")

from components.general.sidebar import render_sidebar

# Дизайн вкладок
render_sidebar()

# Определяем страницы: "Главная" отдельной секцией и блок "Сервисы"
pages = {
    " ": [
        st.Page(
            "pages/home.py",
            title="Главная",
            default=True,
            icon=":material/home:",
        ),
        st.Page(
            "pages/profile.py",
            title="Личный кабинет рекрутера",
            icon=":material/person:",
            url_path="profile",
        ),
    ],
    "Сервисы": [
        st.Page(
            "pages/job_description.py",
            title="Описание вакансии",
            icon=":material/description:",
            url_path="job-description",
        ),
        st.Page(
            "pages/resume_evaluation.py",
            title="Оценка резюме",
            icon=":material/rate_review:",
            url_path="resume-evaluation",
        ),
        st.Page(
            "pages/questions_generation.py",
            title="Генерация вопросов кандидату",
            icon=":material/quiz:",
            url_path="questions",
        ),
    ],
}

# Вставляем навигацию и запускаем выбранную страницу
pg = st.navigation(pages, position="sidebar", expanded=True)
pg.run()

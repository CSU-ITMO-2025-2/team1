import streamlit as st

st.set_page_config(page_title="Генерация вопросов кандидату", page_icon="📊", layout="wide")

from components.general.profile_button import render_profile_button
from services.question_generation import question_generation
from components.question_generation.report import get_report

render_profile_button()

st.title("Генерация вопросов кандидату")


st.caption("Загрузите два файла: **вакансию** и **резюме**. ")

col_vac, col_cv = st.columns(2)
with col_vac:
    vacancy_file = st.file_uploader(
        "Вакансия (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"], key="vacancy_file"
    )
with col_cv:
    resume_file = st.file_uploader(
        "Резюме (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"], key="resume_file"
    )

    # Проверка загрузки файлов
    disabled = not (vacancy_file and resume_file)


# Кнопка оценки
if st.button("Сгенерировать вопросы", disabled=disabled, type="primary"):
    if disabled:
        st.warning("Пожалуйста, загрузите оба файла")
    else:
        with st.spinner("Отправляем на сервер и ждём ответ…"):
            try:
                # Отправляем либо файлы, либо текст
                result_raw = question_generation(
                    vacancy_file=vacancy_file,
                    resume_file=resume_file
                )
                result = result_raw.get("data", result_raw)
            except Exception:
                st.error("Извините, произошла техническая ошибка")
            else:
                st.success("Готово!")
                get_report(result)

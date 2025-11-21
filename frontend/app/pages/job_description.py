"""Страница генерации описания вакансии."""

import streamlit as st
from components.general.profile_button import render_profile_button
from components.general.sidebar import render_sidebar
from components.job_description.result_display import render_job_description_results
from services.job_description import get_vacancy_description
from utils.file_utils import compose_case_input_text

from frontend.app.components.ui.css.submit_button_styles import inject_submit_button_styles

# Боковая панель и кнопка профиля
render_sidebar()
render_profile_button()

# стили для формы
inject_submit_button_styles()

st.title("Генерация описания вакансии")


NS = "jobdesc"  # namespace для ключей страницы


def k(name: str) -> str:
    """Формирует ключ для session_state с namespace."""
    return f"{NS}:{name}"


# --- состояние ---
st.session_state.setdefault(k("result"), None)  # результат выполнения
st.session_state.setdefault(k("uploader_key"), 0)  # id загрузки
st.session_state.setdefault(k("mode"), "Текст")  # тип загрузки
st.session_state.setdefault(k("busy"), False)  # loading для
st.session_state.setdefault(k("pending_mode"), None)
st.session_state.setdefault(k("case_input_text"), "")

busy = st.session_state[k("busy")]

# --- Переменные для входных данных ---
job_input_text = None
job_input_file = None


# --- Выбор типа ввода данных ---
input_mode = st.segmented_control(
    "Выберите способ ввода данных",
    options=["Текст", "Файл"],
    key=k("mode"),
    disabled=busy,
)

# --- форма ввода ---
with st.form(k("form"), border=False):
    if input_mode == "Текст":
        job_input_text = st.text_area(
            "Введите описание вакансии",
            height="content",
            key=k("job_input"),
            max_chars=10000,
            placeholder="На позицию ... требуется ...",
            help=("**Что ввести:** роль, отдел, цели роли; ключевые задачи; требования и набор рабочих инструментов;"),
            disabled=busy,
        )
    else:
        job_input_file = st.file_uploader(
            "Загрузите файл с описанием вакансии (PDF, DOCX, TXT)",
            type=["pdf", "docx", "txt"],
            key=k(f"job_file_{st.session_state[k('uploader_key')]}"),
            help=(
                "**Что добавить в файл:** роль, отдел, цели роли; "
                "ключевые задачи; требования и набор рабочих инструментов;"
            ),
            disabled=busy,
        )

    # Контейнер под кнопку и спиннер
    row = st.container(
        horizontal=True,
        gap="small",
        height=60,
        vertical_alignment="center",
        horizontal_alignment="left",
        border=False,
    )

    with row:
        submitted = st.form_submit_button(
            "Сгенерировать описание",
            type="primary",
            disabled=busy,
        )

    with row:
        spin_slot = st.empty()

# --- генерация ---
if submitted and not busy:
    if input_mode == "Текст" and not st.session_state.get(k("job_input")):
        st.warning("Пожалуйста, введите текст вакансии.")
    elif input_mode == "Файл" and not job_input_file:
        st.warning("Пожалуйста, загрузите файл.")
    else:
        st.session_state[k("pending_mode")] = input_mode
        st.session_state[k("busy")] = True
        st.rerun()

if st.session_state[k("busy")]:
    # показываем спиннер
    with spin_slot, st.spinner("Генерируем описание вакансии…"):
        # собери входные данные
        current_mode = st.session_state.get(k("pending_mode")) or "Текст"
        if current_mode == "Текст":
            text = st.session_state.get(k("job_input"), "")
            file_obj = None
            st.session_state[k("case_input_text")] = compose_case_input_text("Текст", text, None)
        else:
            upload_key = k(f"job_file_{st.session_state[k('uploader_key')]}")
            file_obj = st.session_state.get(upload_key)
            text = None
            st.session_state[k("case_input_text")] = compose_case_input_text("Файл", None, file_obj)

        try:
            result = get_vacancy_description(input_data=text, input_file=file_obj)
            st.session_state[k("result")] = result
        except Exception:
            st.session_state[k("result")] = None
            st.error("Извините, произошла техническая ошибка")

    st.session_state[k("busy")] = False
    st.rerun()


result = st.session_state[k("result")]
if result:
    render_job_description_results(result, NS)

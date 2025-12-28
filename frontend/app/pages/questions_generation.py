import streamlit as st

st.set_page_config(page_title="Генерация вопросов кандидату", page_icon="📊", layout="wide")

from components.general.profile_button import render_profile_button
from services.question_generation import question_generation
from components.question_generation.report import get_report

render_profile_button()

st.title("Генерация вопросов кандидату")

NS = "questions_gen"  # namespace для ключей страницы

def k(name: str) -> str:
    """Формирует ключ для session_state с namespace."""
    return f"{NS}:{name}"

# --- состояние ---
st.session_state.setdefault(k("result"), None)  # результат генерации
st.session_state.setdefault(k("busy"), False)  # флаг обработки запроса
st.session_state.setdefault(k("request_sent"), False)  # флаг отправки запроса

busy = st.session_state[k("busy")]

st.caption("Загрузите два файла: **вакансию** и **резюме**. ")

col_vac, col_cv = st.columns(2)
with col_vac:
    vacancy_file = st.file_uploader(
        "Вакансия (PDF/DOCX/TXT)", 
        type=["pdf", "docx", "txt"], 
        key="vacancy_file",
        disabled=busy
    )
with col_cv:
    resume_file = st.file_uploader(
        "Резюме (PDF/DOCX/TXT)", 
        type=["pdf", "docx", "txt"], 
        key="resume_file",
        disabled=busy
    )

# Проверка загрузки файлов
disabled = not (vacancy_file and resume_file)

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
    # Кнопка только устанавливает флаг
    if st.button("Сгенерировать вопросы", disabled=disabled or busy, type="primary"):
        if disabled:
            st.warning("Пожалуйста, загрузите оба файла")
        else:
            st.session_state[k("busy")] = True
            st.rerun()

with row:
    spin_slot = st.empty()

# Обработка запроса вне блока кнопки
if st.session_state[k("busy")]:
    if not st.session_state[k("request_sent")]:
        st.session_state[k("request_sent")] = True
        
        with spin_slot, st.spinner("Отправляем на сервер и ждём ответ…"):
            try:
                result_raw = question_generation(
                    vacancy_file=vacancy_file,
                    resume_file=resume_file
                )
                result = result_raw.get("data", result_raw)
                st.session_state[k("result")] = result
            except Exception as e:
                st.error(f"Извините, произошла техническая ошибка: {e}")
                st.session_state[k("result")] = None
            finally:
                st.session_state[k("busy")] = False
                st.session_state[k("request_sent")] = False
                st.rerun()

# Отображаем результат
result = st.session_state[k("result")]
if result:
    st.success("Готово!")
    get_report(result)

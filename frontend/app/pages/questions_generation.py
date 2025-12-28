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
st.session_state.setdefault(k("processing"), False)  # флаг обработки запроса
st.session_state.setdefault(k("result"), None)  # результат генерации

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

processing = st.session_state[k("processing")]

# Кнопка оценки
if st.button("Сгенерировать вопросы", disabled=disabled or processing, type="primary"):
    if disabled:
        st.warning("Пожалуйста, загрузите оба файла")
    elif not processing:  # Защита от повторных нажатий
        st.session_state[k("processing")] = True
        with st.spinner("Отправляем на сервер и ждём ответ…"):
            try:
                # Отправляем либо файлы, либо текст
                result_raw = question_generation(
                    vacancy_file=vacancy_file,
                    resume_file=resume_file
                )
                result = result_raw.get("data", result_raw)
                st.session_state[k("result")] = result  # Сохраняем результат
            except Exception as e:
                st.error(f"Извините, произошла техническая ошибка: {e}")
                st.session_state[k("result")] = None  # Очищаем результат при ошибке
            finally:
                st.session_state[k("processing")] = False
                st.rerun()  # Перерисовываем страницу для отображения результата

# Отображаем результат вне блока кнопки
if st.session_state[k("result")] is not None:
    st.success("Готово!")
    get_report(st.session_state[k("result")])

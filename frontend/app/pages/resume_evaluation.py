import streamlit as st

st.set_page_config(page_title="Оценка резюме", page_icon="📊", layout="wide")

from components.general.profile_button import render_profile_button
from components.general.sidebar import render_sidebar
from components.resume_evaluation.format_report_for_pdf import format_resume_report_for_pdf
from components.resume_evaluation.report import get_report
from components.ui.reset_button import reset_button
from components.ui.pdf_button import pdf_download_button
from services.resume_evaluation import resume_evaluation
from utils.pdf_export import build_pdf_bytes
from utils.file_utils import compose_case_input_text

# Дизайн вкладок
render_sidebar()
render_profile_button()

# CSS для исправления обрезки графиков Plotly
st.markdown("""
<style>
/* Контейнеры для графиков Plotly - предотвращаем обрезку */
div[data-testid="stPlotlyChart"] {
    overflow: visible !important;
}

div[data-testid="stPlotlyChart"] > div {
    overflow: visible !important;
}

div[data-testid="stElementContainer"]:has(div[data-testid="stPlotlyChart"]) {
    overflow: visible !important;
}

/* SVG контейнер графика - убираем ограничения */
.svg-container {
    overflow: visible !important;
}

/* Основной контейнер графика */
.plot-container {
    overflow: visible !important;
}

/* Контейнер с ключом для графиков */
div[class*="st-key-"][class*="_donut"],
div[class*="st-key-"][class*="total_donut"],
div[class*="st-key-"][class*="skills_donut"] {
    overflow: visible !important;
}

/* Полноэкранный фрейм графика */
div[data-testid="stFullScreenFrame"] {
    overflow: visible !important;
}

/* Контейнер plotly */
.js-plotly-plot {
    overflow: visible !important;
}
</style>
""", unsafe_allow_html=True)

st.title("Оценка резюме")

NS = "resume_eval"  # namespace для ключей страницы


def k(name: str) -> str:
    """Формирует ключ для session_state с namespace."""
    return f"{NS}:{name}"


# --- состояние ---
st.session_state.setdefault(k("result"), None)  # результат выполнения
st.session_state.setdefault(k("uploader_key"), 0)  # id загрузки
st.session_state.setdefault(k("busy"), False)  # loading
st.session_state.setdefault(k("case_input_text"), "")  # исходные данные
st.session_state.setdefault(k("request_sent"), False)  # флаг отправки запроса

busy = st.session_state[k("busy")]

st.caption("Загрузите два файла: **вакансию** и **резюме**. ")

col_vac, col_cv = st.columns(2)
with col_vac:
    vacancy_file = st.file_uploader(
        "Вакансия (PDF/DOCX/TXT)",
        type=["pdf", "docx", "txt"],
        key=k(f"vacancy_file_{st.session_state[k('uploader_key')]}"),
        disabled=busy,
    )
with col_cv:
    resume_file = st.file_uploader(
        "Резюме (PDF/DOCX/TXT)",
        type=["pdf", "docx", "txt"],
        key=k(f"resume_file_{st.session_state[k('uploader_key')]}"),
        disabled=busy,
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
    # Кнопка оценки
    if st.button("Оценить соответствие", disabled=disabled or busy, type="primary"):
        if disabled:
            st.warning("Пожалуйста, загрузите оба файла.")
        else:
            st.session_state[k("busy")] = True
            st.rerun()

with row:
    spin_slot = st.empty()

if st.session_state[k("busy")]:
    # Проверяем, был ли уже отправлен запрос (защита от дублирования при st.rerun)
    if not st.session_state[k("request_sent")]:
        st.session_state[k("request_sent")] = True  # Устанавливаем флаг
        
        # показываем спиннер
        with spin_slot, st.spinner("Изучаю резюме и вакансию..."):
            # Получаем файлы из session_state
            vacancy_key = k(f"vacancy_file_{st.session_state[k('uploader_key')]}")
            resume_key = k(f"resume_file_{st.session_state[k('uploader_key')]}")
            vac_file = st.session_state.get(vacancy_key)
            res_file = st.session_state.get(resume_key)

            try:
                # Отправляем файлы на сервер
                result_raw = resume_evaluation(
                    vacancy_file=vac_file,
                    resume_file=res_file,
                )
                result = result_raw.get("data", result_raw)

                # Сохраняем результат
                st.session_state[k("result")] = result
                # Сохраняем исходные данные для PDF
                st.session_state[k("case_input_text")] = compose_case_input_text(
                    "Файл",
                    None,
                    vac_file,
                    resume_file=res_file,
                )
            except Exception as e:
                error_message = str(e)
                # Проверяем тип ошибки
                if "422" in error_message or "Unprocessable Entity" in error_message:
                    st.error("❌ Ошибка валидации данных\n\nНе удалось извлечь текст из файлов. Проверьте, что файлы содержат текст и не повреждены.")
                elif "лимит" in error_message.lower() and "токен" in error_message.lower():
                    st.error("❌ Превышен лимит токенов\n\nВакансия и/или резюме слишком большие для обработки.")
                else:
                    st.error(f"❌ Ошибка при оценке резюме: {error_message}")
                st.session_state[k("result")] = None
            finally:
                st.session_state[k("busy")] = False
                st.session_state[k("request_sent")] = False  # Сбрасываем флаг
                st.rerun()

# Отображение результата
result = st.session_state[k("result")]
if result:

    def reset_callback():
        """Очистка результата и перезагрузка загрузчиков файлов."""
        st.session_state[k("result")] = None
        st.session_state[k("uploader_key")] += 1
        st.session_state[k("case_input_text")] = ""
        st.toast("Результат очищен")
        st.rerun()

    # Формируем PDF
    report_text = format_resume_report_for_pdf(result)
    
    # Получаем названия файлов
    vacancy_key = k(f"vacancy_file_{st.session_state[k('uploader_key')]}")
    resume_key = k(f"resume_file_{st.session_state[k('uploader_key')]}")
    vac_file = st.session_state.get(vacancy_key)
    res_file = st.session_state.get(resume_key)
    
    file_names = []
    if vac_file:
        file_names.append(f"Вакансия: {vac_file.name}")
    if res_file:
        file_names.append(f"Резюме: {res_file.name}")
    
    base_context = "\n".join(file_names) if file_names else "Исходные файлы"
    sections = [("Отчет по оценке резюме", report_text)]
    pdf_bytes = build_pdf_bytes(base_context, sections, title="Оценка резюме")

    # Панель с кнопками экспорта и очистки
    with st.container(border=False):
        row = st.container(
            horizontal=True,
            horizontal_alignment="right",
            gap="small",
        )

        with row:
            # Кнопка экспорта в PDF
            pdf_download_button(
                namespace=NS,
                label="Отчет по оценке резюме",
                pdf_bytes=pdf_bytes,
                mode="view",
            )

            # Кнопка очистки результата
            reset_button(
                namespace=NS,
                reset_label="Очистить результат",
                on_reset=reset_callback,
                mode="view",
            )

    # Отображение отчета в контейнере с border
    with st.container(border=True):
        get_report(result)

"""CSS стили для панели кнопок."""

import streamlit as st

PDF_BUTTON_CSS_FLAG = "_jobdesc_pdf_button_css"


def inject_button_panel_styles() -> None:
    """Инжектит CSS, стилизующий кнопки действий."""
    if st.session_state.get(PDF_BUTTON_CSS_FLAG):
        return
    st.session_state[PDF_BUTTON_CSS_FLAG] = True
    st.markdown(
        """
        <style>
        :root {
            --jobdesc-icon-size: 40px;
            --jobdesc-icon-radius: 10px;
            --jobdesc-icon-bg: rgba(15,23,42,.03);
            --jobdesc-icon-border: rgba(15,23,42,.2);
            --jobdesc-icon-hover: rgba(15,23,42,.08);
            --jobdesc-icon-press: rgba(15,23,42,.15);
        }
        button[title="Редактировать"],
        button[title="Экспортировать в PDF"],
        button[title="Экспорт текущей редакции в PDF"],
        button[title="Очистить результат"],
        button[title="Сохранить"],
        button[title="Отменить"],
        button[title="Скопировать секцию"],
        button[title="Скопировать текущую редакцию"],
        button[title="Копировать"],
        div[data-testid="stDownloadButton"] button,
        .copy-chip-wrapper,
        .copy-chip-wrapper button,
        .st-copy-btn {
            border-radius: var(--jobdesc-icon-radius) !important;
            border: 1px solid var(--jobdesc-icon-border) !important;
            background: var(--jobdesc-icon-bg) !important;
            color: #0f172a !important;
            box-shadow: none !important;
            padding: 0 !important;
            min-height: var(--jobdesc-icon-size) !important;
            height: var(--jobdesc-icon-size) !important;
            min-width: var(--jobdesc-icon-size) !important;
            width: var(--jobdesc-icon-size) !important;
            max-width: var(--jobdesc-icon-size) !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            transition: all .2s ease !important;
            margin: 0 !important;
            cursor: pointer !important;
        }
        button.st-copy-btn svg {
            width: 26px !important;
            height: 26px !important;
        }
        button.st-copy-btn .st-copy-label {
            display: none !important;
        }
        button[type="primary"][title="Сохранить"] {
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
            color: #fff !important;
            border-color: #2563eb !important;
            box-shadow: 0 2px 8px rgba(37,99,235,.2) !important;
        }
        button[title="Редактировать"]:hover,
        button[title="Экспортировать в PDF"]:hover,
        button[title="Экспорт текущей редакции в PDF"]:hover,
        button[title="Очистить результат"]:hover,
        button[title="Сохранить"]:hover,
        button[title="Отменить"]:hover,
        button[title="Скопировать секцию"]:hover,
        button[title="Скопировать текущую редакцию"]:hover,
        button[title="Копировать"]:hover,
        div[data-testid="stDownloadButton"] button:hover,
        .copy-chip-wrapper:hover,
        .copy-chip-wrapper button:hover,
        .st-copy-btn:hover {
            background: var(--jobdesc-icon-hover) !important;
            transform: translateY(-1px) !important;
            box-shadow: none !important;
            border-color: rgba(15,23,42,.3) !important;
        }
        button[type="primary"][title="Сохранить"]:hover {
            box-shadow: 0 4px 14px rgba(37,99,235,.3) !important;
        }
        button[title="Редактировать"]:active,
        button[title="Экспортировать в PDF"]:active,
        button[title="Экспорт текущей редакции в PDF"]:active,
        button[title="Очистить результат"]:active,
        button[title="Сохранить"]:active,
        button[title="Отменить"]:active,
        button[title="Скопировать секцию"]:active,
        button[title="Скопировать текущую редакцию"]:active,
        button[title="Копировать"]:active,
        div[data-testid="stDownloadButton"] button:active,
        .copy-chip-wrapper button:active,
        .st-copy-btn:active {
            background: var(--jobdesc-icon-press) !important;
            transform: translateY(0) !important;
        }
        button[title="Редактировать"] p,
        button[title="Сохранить"] p,
        button[title="Отменить"] p,
        button[title="Очистить результат"] p,
        button[title="Копировать"] p,
        button[title="Редактировать"] div[data-testid="stMarkdownContainer"],
        button[title="Сохранить"] div[data-testid="stMarkdownContainer"],
        button[title="Отменить"] div[data-testid="stMarkdownContainer"],
        button[title="Очистить результат"] div[data-testid="stMarkdownContainer"] {
            display: none !important;
        }
        button[title="Редактировать"] svg,
        button[title="Сохранить"] svg,
        button[title="Отменить"] svg,
        button[title="Очистить результат"] svg,
        button[title="Копировать"] svg {
            width: 20px !important;
            height: 20px !important;
            margin: 0 !important;
        }
        .st-copy-btn svg,
        .st-copy-btn img {
            width: 20px !important;
            height: 20px !important;
            flex-shrink: 0;
            margin: 0 !important;
            object-fit: contain !important;
        }
        .st-copy-btn .copy-chip-content {
            padding: 0 !important;
            width: 100% !important;
            height: 100% !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        /* Стили для кнопки копирования из st.code */
        div[data-testid="stCodeBlock"] button[data-testid="stCodeBlockCopyButton"],
        div[data-testid="stCodeBlock"] button[aria-label*="Copy"] {
            width: var(--jobdesc-icon-size) !important;
            min-width: var(--jobdesc-icon-size) !important;
            height: var(--jobdesc-icon-size) !important;
            min-height: var(--jobdesc-icon-size) !important;
            border-radius: var(--jobdesc-icon-radius) !important;
            border: 1px solid var(--jobdesc-icon-border) !important;
            background: var(--jobdesc-icon-bg) !important;
            color: #0f172a !important;
            box-shadow: none !important;
            padding: 0 !important;
            margin: 0 !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            transition: all .2s ease !important;
            cursor: pointer !important;
        }
        div[data-testid="stCodeBlock"] button[data-testid="stCodeBlockCopyButton"]:hover,
        div[data-testid="stCodeBlock"] button[aria-label*="Copy"]:hover {
            background: var(--jobdesc-icon-hover) !important;
            transform: translateY(-1px) !important;
            border-color: rgba(15,23,42,.3) !important;
        }
        div[data-testid="stCodeBlock"] button[data-testid="stCodeBlockCopyButton"]:active,
        div[data-testid="stCodeBlock"] button[aria-label*="Copy"]:active {
            background: var(--jobdesc-icon-press) !important;
            transform: translateY(0) !important;
        }
        /* Убираем лишние отступы у вкладок */
        div[data-testid="stTabs"] > div[role="tabpanel"] {
            padding-top: 0 !important;
        }
        div[data-testid="stTabs"] > div[role="tabpanel"] > div {
            padding-top: 0 !important;
        }
        /* Растягиваем горизонтальные контейнеры с кнопками на всю ширину */
        div[data-testid="stTabs"] div[data-testid="stHorizontalBlock"]:has(button[title*="PDF"]),
        div[data-testid="stTabs"] div[data-testid="stHorizontalBlock"]:has(button[title="Редактировать"]),
        div[role="tabpanel"] div[data-testid="stHorizontalBlock"]:has(button[title*="PDF"]),
        div[role="tabpanel"] div[data-testid="stHorizontalBlock"]:has(button[title="Редактировать"]) {
            width: 100% !important;
            max-width: 100% !important;
        }
        /* Обеспечиваем правильное flex-выравнивание для основного контейнера с кнопками */
        div[data-testid="stVerticalBlockBorderWrapper"]:has(
            > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"]:has(button[title*="PDF"])
        ) > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"],
        div[data-testid="stTabs"] div[data-testid="stVerticalBlockBorderWrapper"]:has(
            > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"]:has(button[title*="PDF"])
        ) > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"],
        div[role="tabpanel"] div[data-testid="stVerticalBlockBorderWrapper"]:has(
            > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"]:has(button[title*="PDF"])
        ) > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] {
            display: flex !important;
            justify-content: space-between !important;
            align-items: center !important;
            width: 100% !important;
            max-width: 100% !important;
            gap: 8px !important;
            flex-flow: row nowrap !important;
            flex: 1 1 auto !important;
        }
        /* Фиксируем левую часть с кнопками копирования и редактирования */
        div[data-testid="stHorizontalBlock"]:has(button[title="Копировать"])
            > div[data-testid="stElementContainer"]:first-child,
        div[data-testid="stHorizontalBlock"]:has(button[title="Редактировать"])
            > div[data-testid="stElementContainer"]:has(button[title="Копировать"]),
        div[data-testid="stHorizontalBlock"]:has(button[title="Редактировать"])
            > div[data-testid="stElementContainer"]:has(button[title="Редактировать"]) {
            flex: 0 0 auto !important;
            flex-shrink: 0 !important;
            flex-grow: 0 !important;
            width: fit-content !important;
            min-width: fit-content !important;
            max-width: fit-content !important;
        }
        /* Выравниваем правые кнопки в конец контейнера */
        div[data-testid="stHorizontalBlock"]:has(button[title*="PDF"])
            > div[data-testid="stHorizontalBlock"]:has(button[title*="PDF"]),
        div[data-testid="stTabs"] div[data-testid="stHorizontalBlock"]:has(button[title*="PDF"])
            > div[data-testid="stHorizontalBlock"]:has(button[title*="PDF"]),
        div[role="tabpanel"] div[data-testid="stHorizontalBlock"]:has(button[title*="PDF"])
            > div[data-testid="stHorizontalBlock"]:has(button[title*="PDF"]) {
            flex-shrink: 0 !important;
            margin-left: auto !important;
            width: auto !important;
            max-width: none !important;
            justify-content: flex-start !important;
            align-items: center !important;
            flex-flow: row nowrap !important;
        }
        /* Растягиваем пространство между кнопками */
        div[data-testid="stHorizontalBlock"]:has(button[title*="PDF"])
            > div[data-testid="stSpacer"],
        div[data-testid="stTabs"] div[data-testid="stHorizontalBlock"]:has(button[title*="PDF"])
            > div[data-testid="stSpacer"],
        div[role="tabpanel"] div[data-testid="stHorizontalBlock"]:has(button[title*="PDF"])
            > div[data-testid="stSpacer"] {
            flex: 1 1 auto !important;
            min-width: 0 !important;
        }
        /* Скрываем iframe от streamlit_js_eval */
        /* Скрываем контейнер с ключом _js */
        div[class*="st-key-"][class*="_js"] {
            display: none !important;
            width: 0 !important;
            height: 0 !important;
            flex: 0 0 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            position: absolute !important;
            visibility: hidden !important;
            overflow: hidden !important;
        }
        /* Убеждаемся, что кнопки не растягиваются и имеют фиксированную ширину */
        div[data-testid="stHorizontalBlock"]:has(button[title="Копировать"]) button,
        div[data-testid="stHorizontalBlock"]:has(button[title="Редактировать"]) button,
        div[data-testid="stHorizontalBlock"]:has(button[title="Копировать"])
            > div[data-testid="stElementContainer"],
        div[data-testid="stHorizontalBlock"]:has(button[title="Редактировать"])
            > div[data-testid="stElementContainer"] {
            flex-shrink: 0 !important;
            flex-grow: 0 !important;
            width: auto !important;
            min-width: auto !important;
            max-width: none !important;
        }
        /* Фиксируем контейнеры с кнопками, чтобы они не смещались */
        div[data-testid="stHorizontalBlock"]:has(button[title="Копировать"])
            > div[data-testid="stElementContainer"]:has(button[title="Копировать"]),
        div[data-testid="stHorizontalBlock"]:has(button[title="Редактировать"])
            > div[data-testid="stElementContainer"]:has(button[title="Редактировать"]) {
            flex: 0 0 auto !important;
            width: fit-content !important;
        }
        /* Скрываем рамку у контейнера с кнопками, но сохраняем его ширину */
        div[data-testid="stVerticalBlockBorderWrapper"]:has(
            > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"]:has(button[title*="PDF"])
        ),
        div[data-testid="stVerticalBlockBorderWrapper"]:has(
            > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"]:has(button[title="Редактировать"])
        ),
        div[data-testid="stTabs"] div[data-testid="stVerticalBlockBorderWrapper"]:has(
            > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"]:has(button[title*="PDF"])
        ),
        div[data-testid="stTabs"] div[data-testid="stVerticalBlockBorderWrapper"]:has(
            > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"]:has(button[title="Редактировать"])
        ),
        div[role="tabpanel"] div[data-testid="stVerticalBlockBorderWrapper"]:has(
            > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"]:has(button[title*="PDF"])
        ),
        div[role="tabpanel"] div[data-testid="stVerticalBlockBorderWrapper"]:has(
            > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"]:has(button[title="Редактировать"])
        ) {
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
            padding: 0 !important;
            margin-bottom: 8px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def inject_md_card_styles(height: int = 720, tone: str = "neutral") -> None:
    """Инжектит CSS стили для карточки markdown."""
    bg_map = {
        "neutral": st.get_option("theme.secondaryBackgroundColor"),
        "blue": "rgba(59,130,246,.08)",
        "green": "rgba(16,185,129,.08)",
    }
    border = "rgba(100,116,139,.18)"
    bg = bg_map.get(tone, bg_map["neutral"])

    st.markdown(
        f"""
        <style>
        /* окрас ближайшего «обёртки» контейнера с рамкой */
        div[data-testid="stVerticalBlockBorderWrapper"]:has(
            > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"]
        ) {{
            background: {bg};
            border: 1px solid {border};
            border-radius: 14px;
            box-shadow: 0 6px 18px rgba(0,0,0,.04);
            max-height: {height}px;
            overflow: auto;
        }}

        /* Padding для markdown контейнера */
        div[data-testid="stVerticalBlockBorderWrapper"]:has(
            > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"]
        ) div[data-testid="stMarkdownContainer"] {{
            padding: 12px 14px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

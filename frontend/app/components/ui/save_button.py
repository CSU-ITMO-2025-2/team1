"""Компонент кнопки сохранения."""

import streamlit as st


def save_button(
    namespace: str,
    work_key: str,
    txt_key: str,
    edit_key: str,
) -> bool:
    """Отображает кнопку сохранения.

    Args:
        namespace: Пространство имен для ключей
        work_key: Ключ для рабочего текста в session_state
        txt_key: Ключ для сохраненного текста в session_state
        edit_key: Ключ для состояния редактирования

    Returns:
        True если кнопка была нажата, иначе False

    """
    if st.button(
        "",
        icon=":material/check:",
        type="primary",
        help="Сохранить",
        key=f"{namespace}:save",
        use_container_width=False,
    ):
        st.session_state[txt_key] = st.session_state[work_key]
        st.session_state[edit_key] = False
        st.toast("Сохранено")
        st.rerun()
        return True
    return False


"""Утилиты для работы с cookies."""
import os
from typing import Dict, Optional
import streamlit as st
from streamlit_js_eval import streamlit_js_eval


def get_cookies() -> Dict[str, str]:
    """
    Получить cookies из браузера через JavaScript.
    
    Returns:
        Dict[str, str]: Словарь с cookies
    """
    # Используем JavaScript для получения cookies
    js_code = """
    (function() {
        const cookies = {};
        document.cookie.split(';').forEach(cookie => {
            const [name, value] = cookie.trim().split('=');
            if (name && value) {
                cookies[name] = value;
            }
        });
        return JSON.stringify(cookies);
    })()
    """
    
    try:
        result = streamlit_js_eval(
            js_expressions=js_code,
            key="get_cookies",
            want_output=True,
        )
        
        if result:
            import json
            return json.loads(result)
    except Exception as e:
        st.warning(f"Не удалось получить cookies: {e}")
    
    return {}


def get_session_cookie() -> Optional[str]:
    """
    Получить session cookie (sid) для авторизации.
    
    Returns:
        Optional[str]: Значение cookie 'sid' или None
    """
    cookie_name = os.getenv("AUTH_COOKIE_NAME", "sid")
    
    # Пробуем получить из session_state (кэш)
    if f"_cookie_{cookie_name}" in st.session_state:
        return st.session_state[f"_cookie_{cookie_name}"]
    
    # Получаем из браузера
    cookies = get_cookies()
    sid = cookies.get(cookie_name)
    
    # Кэшируем в session_state
    if sid:
        st.session_state[f"_cookie_{cookie_name}"] = sid
    
    return sid


def prepare_request_cookies() -> Dict[str, str]:
    """
    Подготовить cookies для отправки в запросе к core_api.
    
    Returns:
        Dict[str, str]: Словарь с cookies для requests
    """
    cookie_name = os.getenv("AUTH_COOKIE_NAME", "sid")
    sid = get_session_cookie()
    
    if sid:
        return {cookie_name: sid}
    
    return {}


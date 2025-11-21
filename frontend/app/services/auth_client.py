"""
Клиент для работы с Auth BFF Service.

Упрощенная версия, полагающаяся на cookie-based аутентификацию.
"""

import os, json
from typing import Optional
import streamlit as st
from dotenv import load_dotenv
from streamlit_js_eval import streamlit_js_eval 

load_dotenv()

# Конфигурация
AUTH_BASE = os.getenv("AUTH_PUBLIC_URL", "http://10.128.65.21/auth").rstrip("/")
DEBUG_AUTH = os.getenv("DEBUG_AUTH", "false").lower() == "true"
REQUEST_TIMEOUT = 5


def _dbg(msg: str, **kwargs) -> None:
    """Отладочное логирование."""
    if not DEBUG_AUTH:
        return
    details = " | ".join(f"{k}={v}" for k, v in kwargs.items()) if kwargs else ""
    print(f"[auth_client] {msg} {details}")


def login_link(next_path: Optional[str] = None) -> str:
    base = f"{AUTH_BASE}/login"
    return f"{base}?next={next_path}" if next_path else base


def logout_link() -> str:
    """
    Формирование ссылки на логаут.
    
    Returns:
        URL для логаута
    """
    return f"{AUTH_BASE}/logout"


def load_user_once() -> Optional[dict]:
    # Если уже получали ранее
    if "user" in st.session_state:
        return st.session_state["user"]

    # вызов компонента за прогон
    js = f"""
    (async () => {{
      try {{
        const r = await fetch("{AUTH_BASE}/me", {{ credentials: "include" }});
        if (!r.ok) return null;           // 401 -> не залогинен
        const u = await r.json();
        return JSON.stringify(u);
      }} catch (e) {{ return null; }}
    }})()
    """

    data = streamlit_js_eval(
        js_expressions=js,
        key="auth_me",
        label="auth_me",
        want_output=True,
    )

    if data:
        user = json.loads(data)
        st.session_state["user"] = user
        return user
    return None


def get_compact_name(full_name: str) -> str:
    """
    Формирование компактного имени (Фамилия И.О.).
    
    Args:
        full_name: Полное имя
        
    Returns:
        Компактное представление имени
    """
    if not full_name:
        return ""
    
    parts = [p.strip() for p in full_name.split() if p.strip()]
    if not parts:
        return ""
    
    # Берем первую часть (фамилию)
    result = parts[0]
    
    # Добавляем инициалы
    if len(parts) >= 2:
        result += f" {parts[1][0]}."

    return result

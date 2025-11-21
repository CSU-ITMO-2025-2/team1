"""
Auth BFF Service для HR-Assist.

Минимальный Backend-For-Frontend сервис для аутентификации через OIDC/OAuth2.
Использует in-memory хранение сессий (для продакшена рекомендуется Redis).
"""

import json
import os
import secrets
import time
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlencode

import httpx
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse, RedirectResponse

# Загрузка переменных окружения
load_dotenv()

# Импорт логгера
from logger import get_logger, setup_logging

setup_logging(os.getenv("LOG_LEVEL", "INFO"))
log = get_logger("auth_bff")


# ==================== КОНФИГУРАЦИЯ ====================

# Основные параметры сервиса
PORT = int(os.getenv("AUTH_PORT", "9000"))
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://10.128.65.21:8501").rstrip("/")
AUTH_PUBLIC_URL = os.getenv("AUTH_PUBLIC_URL", f"{FRONTEND_URL}/auth").rstrip("/")

# OIDC/OAuth2 параметры
ISSUER = os.getenv(
    "OIDC_ISSUER", "https://keycloak-vld.fesco.com/realms/master"
).rstrip("/")
KC_CLIENT_ID = os.getenv("KC_CLIENT_ID", "hr-assist-bff")
KC_CLIENT_SECRET = os.getenv("KC_CLIENT_SECRET", "CHANGE_ME")
SCOPES = os.getenv("SCOPES", "openid profile email")

# Cookie параметры
COOKIE_NAME = os.getenv("COOKIE_NAME", "sid")
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "Lax")

# Параметры сессии
SESSION_TTL_SECONDS = int(os.getenv("SESSION_TTL_SECONDS", "3600"))
STATE_TTL_SECONDS = 300  # 5 минут на прохождение авторизации

REQUIRED_GROUPS = ["/gr-vld-hr-assist-admin", "/gr-vld-hr-assist-recruter", "/gr-vld-hr-assist-super-recruter"]

GROUP_LABELS = {
    "/gr-vld-hr-assist-admin": "админ",
    "/gr-vld-hr-assist-recruter": "рекрутер",
    "/gr-vld-hr-assist-super-recruter": "супер-рекрутер"
}

# Формирование правильного redirect_uri
REDIRECT_URI = f"{AUTH_PUBLIC_URL}/callback"

# Логирование конфигурации при старте
log.info(
    "Конфигурация: PORT=%s, FRONTEND_URL=%s, AUTH_PUBLIC_URL=%s, REDIRECT_URI=%s",
    PORT,
    FRONTEND_URL,
    AUTH_PUBLIC_URL,
    REDIRECT_URI,
)


# ==================== OIDC DISCOVERY ====================


def discover_oidc_endpoints() -> Tuple[str, str, str, Optional[str]]:
    """
    Получение OIDC endpoints через discovery.

    Returns:
        Tuple из (authorization_endpoint, token_endpoint, userinfo_endpoint, logout_endpoint)
    """
    try:
        with httpx.Client(timeout=10) as client:
            response = client.get(f"{ISSUER}/.well-known/openid-configuration")
            response.raise_for_status()
            well_known = response.json()

            auth_url = well_known["authorization_endpoint"]
            token_url = well_known["token_endpoint"]
            userinfo_url = well_known["userinfo_endpoint"]
            logout_url = well_known.get("end_session_endpoint")  # Опционально

            log.info(
                "OIDC Discovery успешно: auth=%s, token=%s, userinfo=%s, logout=%s",
                auth_url,
                token_url,
                userinfo_url,
                logout_url,
            )

            return auth_url, token_url, userinfo_url, logout_url

    except Exception as e:
        log.error("Ошибка OIDC Discovery: %s", e)
        raise


# Получаем OIDC endpoints при старте
AUTH_URL, TOKEN_URL, USERINFO_URL, LOGOUT_URL = discover_oidc_endpoints()


# ==================== ХРАНИЛИЩА ДАННЫХ ====================

# In-memory хранилища
# state -> {expires_at, next_path}
STATE_STORE: Dict[str, Dict[str, Any]] = {}
# sid -> {token, userinfo, expires_at}
SESSION_STORE: Dict[str, Dict[str, Any]] = {}


# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================


def _now() -> float:
    """Получение текущего времени в Unix timestamp."""
    return time.time()


def _clean_expired_data() -> None:
    """
    Очистка истекших state и сессий.

    Удаляет записи, у которых истекло время жизни.
    """
    current_time = _now()

    # Очистка истекших state
    expired_states = [
        state
        for state, data in STATE_STORE.items()
        if data.get("expires_at", 0) < current_time
    ]
    for state in expired_states:
        STATE_STORE.pop(state, None)
        log.debug("Удален истекший state: %s", state)

    # Очистка истекших сессий
    expired_sessions = [
        sid
        for sid, data in SESSION_STORE.items()
        if data.get("expires_at", 0) < current_time
    ]
    for sid in expired_sessions:
        SESSION_STORE.pop(sid, None)
        log.debug("Удалена истекшая сессия: %s", sid)


def _set_sid_cookie(response: Response, sid: str) -> None:
    """
    Установка cookie с идентификатором сессии.

    Args:
        response: FastAPI Response объект
        sid: Идентификатор сессии
    """
    response.set_cookie(
        key=COOKIE_NAME,
        value=sid,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        path="/auth",  # Важно: ограничиваем путь до /auth
        max_age=SESSION_TTL_SECONDS,
    )
    log.debug(
        "Cookie установлен: name=%s, path=/auth, secure=%s", COOKIE_NAME, COOKIE_SECURE
    )


def _delete_sid_cookie(response: Response) -> None:
    """
    Удаление cookie с идентификатором сессии.

    Args:
        response: FastAPI Response объект
    """
    response.delete_cookie(
        key=COOKIE_NAME,
        path="/auth",  # Важно: путь должен совпадать с установкой
    )
    log.debug("Cookie удален: name=%s, path=/auth", COOKIE_NAME)


# ==================== ИНИЦИАЛИЗАЦИЯ ПРИЛОЖЕНИЯ ====================

app = FastAPI(
    title="HR-Assist Auth BFF",
    description="Backend-For-Frontend сервис для аутентификации",
    version="1.0.0",
    root_path="/auth",
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,  # Обязательно для работы с cookies
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# ==================== МАРШРУТЫ ====================


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Проверка состояния сервиса.

    Returns:
        Статус сервиса
    """
    return {"status": "healthy", "service": "auth_bff", "timestamp": _now()}


@app.get("/login")
async def login(next: Optional[str] = None) -> RedirectResponse:
    """
    Инициация процесса авторизации через OIDC.

    Args:
        next: URL для редиректа после успешной авторизации

    Returns:
        Редирект на authorization endpoint провайдера
    """
    _clean_expired_data()

    # Генерация уникального state для защиты от CSRF
    state = secrets.token_urlsafe(24)

    # Сохранение state с временем истечения и next_path
    STATE_STORE[state] = {
        "expires_at": _now() + STATE_TTL_SECONDS,
        "next_path": next or "/",
    }

    # Формирование параметров для authorization request
    params = {
        "response_type": "code",
        "client_id": KC_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
        "state": state,
    }

    authorization_url = f"{AUTH_URL}?{urlencode(params)}"

    log.info(
        "Инициирован login: state=%s, next=%s, redirect_to=%s",
        state,
        next,
        authorization_url,
    )

    return RedirectResponse(url=authorization_url, status_code=302)


@app.get("/callback")
async def callback(
    code: Optional[str] = None, state: Optional[str] = None
) -> RedirectResponse:
    """
    Callback для обработки ответа от OIDC провайдера.

    Args:
        code: Authorization code от провайдера
        state: State параметр для защиты от CSRF

    Returns:
        Редирект на фронтенд с установленной сессией

    Raises:
        HTTPException: При ошибках валидации или обмена токенов
    """
    _clean_expired_data()

    # Валидация параметров
    if not code or not state:
        log.warning("Callback без code или state")
        raise HTTPException(
            status_code=400, detail="Отсутствуют обязательные параметры"
        )

    # Проверка state
    state_data = STATE_STORE.pop(state, None)
    if not state_data:
        log.warning("Неизвестный или истекший state: %s", state)
        raise HTTPException(status_code=400, detail="Недействительный state параметр")

    next_path = state_data.get("next_path", "/")

    try:
        # Обмен authorization code на токены
        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "client_id": KC_CLIENT_ID,
            "client_secret": KC_CLIENT_SECRET,
        }

        with httpx.Client(timeout=10) as client:
            # Получение токенов
            token_response = client.post(TOKEN_URL, data=token_data)
            if token_response.status_code != 200:
                log.error("Ошибка обмена токенов: %s", token_response.text)
                raise HTTPException(
                    status_code=401,
                    detail=f"Ошибка обмена токенов: {token_response.status_code}",
                )

            tokens = token_response.json()

            # Получение информации о пользователе
            userinfo_response = client.get(
                USERINFO_URL,
                headers={"Authorization": f"Bearer {tokens['access_token']}"},
            )
            if userinfo_response.status_code != 200:
                log.error("Ошибка получения userinfo: %s", userinfo_response.text)
                raise HTTPException(
                    status_code=401,
                    detail="Не удалось получить информацию о пользователе",
                )

            userinfo = userinfo_response.json()

        # Создание сессии
        sid = secrets.token_urlsafe(24)
        SESSION_STORE[sid] = {
            "tokens": tokens,
            "userinfo": userinfo,
            "expires_at": _now() + SESSION_TTL_SECONDS,
            "created_at": _now(),
        }

        log.info(
            "Успешная авторизация: sid=%s, user=%s, expires_in=%s",
            sid,
            userinfo.get("preferred_username", userinfo.get("sub")),
            SESSION_TTL_SECONDS,
        )

        # Формирование URL для редиректа
        redirect_url = f"{FRONTEND_URL}{next_path}"
        response = RedirectResponse(url=redirect_url, status_code=302)

        # Установка cookie
        _set_sid_cookie(response, sid)

        return response

    except HTTPException:
        raise
    except Exception as e:
        log.error("Неожиданная ошибка в callback: %s", e)
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@app.get("/me")
async def get_current_user(request: Request) -> Dict[str, Any]:
    """
    Получение информации о текущем пользователе.

    Args:
        request: FastAPI Request объект

    Returns:
        Информация о пользователе

    Raises:
        HTTPException: Если пользователь не авторизован
    """
    # Получение sid из cookie
    sid = request.cookies.get(COOKIE_NAME)

    if not sid:
        log.debug("Запрос /me без cookie")
        return JSONResponse(
            content={"error": "unauthorized", "message": "Отсутствует сессия"},
            status_code=401,
        )

    # Поиск сессии
    session = SESSION_STORE.get(sid)

    if not session:
        log.debug("Сессия не найдена для sid: %s", sid)
        return JSONResponse(
            content={"error": "unauthorized", "message": "Недействительная сессия"},
            status_code=401,
        )

    # Проверка истечения сессии
    if session.get("expires_at", 0) < _now():
        log.debug("Сессия истекла: sid=%s", sid)
        SESSION_STORE.pop(sid, None)
        return JSONResponse(
            content={"error": "unauthorized", "message": "Сессия истекла"},
            status_code=401,
        )

    userinfo = session.get("userinfo", {})

    log.debug(
        "Запрос /me успешен: user=%s",
        userinfo.get("preferred_username", userinfo.get("sub")),
    )

    # Получим группы пользователя
    raw_groups = userinfo.get("group", [])  # ожидаем, что mapper настроен и группы есть
    if not isinstance(raw_groups, list):
        raw_groups = []

    # Отбираем только разрешённые
    allowed_kc_groups = [g for g in raw_groups if g in REQUIRED_GROUPS]

    # Переводим в человеко-читаемые значения
    allowed_user_groups = [GROUP_LABELS[g] for g in allowed_kc_groups]

    log.info(f"Группы пользователя {allowed_user_groups}")

    # Проверка: есть ли пересечение с REQUIRED_GROUPS
    has_access = True if allowed_user_groups else False

    # Возвращаем только необходимую информацию
    return {
        "preferred_username": userinfo.get("preferred_username"),
        "email": userinfo.get("email"),
        "sub": userinfo.get("sub"),
        "name": userinfo.get("name"),
        "given_name": userinfo.get("given_name"),
        "family_name": userinfo.get("family_name"),
        "has_access": has_access,
        "groups": allowed_user_groups
    }


@app.api_route("/logout", methods=["GET", "POST"])
async def logout(request: Request) -> RedirectResponse:
    """
    Выход из системы.

    Удаляет сессию и cookie, опционально редиректит на logout endpoint провайдера.

    Args:
        request: FastAPI Request объект

    Returns:
        Редирект на фронтенд или logout endpoint провайдера
    """
    # Получение и удаление сессии
    sid = request.cookies.get(COOKIE_NAME)
    if sid:
        session = SESSION_STORE.pop(sid, None)
        if session:
            user = session.get("userinfo", {})
            log.info(
                "Logout: user=%s, sid=%s",
                user.get("preferred_username", user.get("sub")),
                sid,
            )

    # Если есть logout endpoint у провайдера
    if LOGOUT_URL:
        logout_params = {
            "post_logout_redirect_uri": FRONTEND_URL,
            # Можно добавить id_token_hint если нужно
        }
        provider_logout_url = f"{LOGOUT_URL}?{urlencode(logout_params)}"
        response = RedirectResponse(url=provider_logout_url, status_code=302)
    else:
        response = RedirectResponse(url=FRONTEND_URL, status_code=302)

    # Удаление cookie
    _delete_sid_cookie(response)

    return response


@app.options("/{path:path}")
async def preflight_handler(request: Request) -> PlainTextResponse:
    """
    Обработчик preflight CORS запросов.

    Args:
        request: FastAPI Request объект

    Returns:
        Ответ с CORS заголовками
    """
    response = PlainTextResponse("OK", status_code=200)
    response.headers["Access-Control-Allow-Origin"] = FRONTEND_URL
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


# ==================== ТОЧКА ВХОДА ====================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=PORT,
        reload=True,
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
    )

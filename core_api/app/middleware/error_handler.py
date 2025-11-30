"""Middleware для централизованной обработки ошибок."""
import time
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.logger import setup_logger

logger = setup_logger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware для обработки всех необработанных ошибок."""
    
    async def dispatch(self, request: Request, call_next):
        """
        Обработать запрос и перехватить ошибки.
        
        Args:
            request: HTTP запрос
            call_next: Следующий обработчик в цепочке
            
        Returns:
            Response: HTTP ответ
        """
        start_time = time.time()
        
        try:
            response = await call_next(request)
            return response
        
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            
            logger.error(
                "Необработанная ошибка в middleware",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "error_type": type(e).__name__,
                    "error": str(e),
                    "latency_ms": latency_ms
                },
                exc_info=True
            )
            
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "detail": "Внутренняя ошибка сервера",
                    "error": str(e)
                }
            )


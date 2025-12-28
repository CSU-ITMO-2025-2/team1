"""
RabbitMQ клиент для асинхронного взаимодействия с микросервисами

"""

import asyncio
import json
import uuid
from typing import Any, Dict

import aio_pika

from app.logger import setup_logger

# Логирование
logger = setup_logger(__name__)


class RabbitMQClient:
    """
    Клиент для асинхронного взаимодействия с RabbitMQ.
    
    Attributes:
        rabbit_url (str): URL подключения к RabbitMQ
        connection: Активное соединение с RabbitMQ
        channel: Канал для отправки сообщений
        pending_responses: Словарь для хранения ожидающих ответов по correlation_id
        logger: Логгер для записи событий
    """
    
    def __init__(self, rabbit_url: str):
        """
        Инициализация клиента RabbitMQ.
        
        Args:
            rabbit_url (str): URL для подключения к RabbitMQ серверу
        """
        self.rabbit_url = rabbit_url
        self.connection = None
        self.channel = None
        self.pending_responses = {}  # {correlation_id: response_body}
        self.logger = setup_logger(__name__)
        self.logger.info(
            "Инициализация клиента RabbitMQ",
            extra={"url": self.rabbit_url.replace(":guest@", ":***@")}
        )

    async def connect(self):
        """
        Установка соединения с RabbitMQ.
        
        Выполняет:
        1. Подключение к серверу RabbitMQ
        2. Создание канала
        
        Raises:
            Exception: При ошибке подключения к RabbitMQ
        """
        try:
            self.logger.info("Подключение к RabbitMQ")
            self.logger.debug(
                f"🔍 [RABBITMQ] URL: {self.rabbit_url.replace(':guest@', ':***@')}"
            )
            self.logger.debug("🔍 [RABBITMQ] Вызов aio_pika.connect_robust...")

            self.connection = await aio_pika.connect_robust(
                self.rabbit_url,
                heartbeat=600,  # 10 минут
            )
            self.logger.debug(
                f"🔍 [RABBITMQ] Соединение установлено: {self.connection}"
            )

            self.logger.debug("🔍 [RABBITMQ] Создание канала...")
            self.channel = await self.connection.channel()
            self.logger.debug(f"🔍 [RABBITMQ] Канал создан: {self.channel}")

            self.logger.info("Успешное подключение к RabbitMQ")
        except Exception as e:
            self.logger.debug(
                f"🔍 [RABBITMQ] ❌ Ошибка подключения: {type(e).__name__}: {e}"
            )
            self.logger.error(f"Ошибка подключения к RabbitMQ: {str(e)}", exc_info=True)
            raise

    async def _on_response(
        self, correlation_id: str, message: aio_pika.IncomingMessage
    ):
        """
        Обработчик входящих сообщений для конкретного correlation_id.
        
        Args:
            correlation_id: Ожидаемый correlation_id
            message (aio_pika.IncomingMessage): Входящее сообщение от RabbitMQ
        """
        msg_corr_id = message.correlation_id
        self.logger.debug(
            f"🔍 [RABBITMQ] Получено сообщение с correlation_id: {msg_corr_id}",
            extra={"correlation_id": msg_corr_id, "expected": correlation_id},
        )

        # Сохраняем ответ только если correlation_id совпадает
        if msg_corr_id == correlation_id:
            self.logger.debug(
                f"🔍 [RABBITMQ] ✅ Сохраняем ответ для correlation_id: {correlation_id}",
                extra={"correlation_id": correlation_id},
            )
            self.pending_responses[correlation_id] = message.body
            await message.ack()
        else:
            self.logger.warning(
                f"🔍 [RABBITMQ] ⚠️ Получен ответ с неожиданным correlation_id: {msg_corr_id}, ожидался: {correlation_id}",
                extra={"received": msg_corr_id, "expected": correlation_id},
            )
            await message.reject(requeue=True)

    async def call(
        self, payload: Dict[str, Any], queue_name: str = "resume_evaluation_task"
    ) -> Dict[str, Any]:
        """
        Отправка RPC запроса в RabbitMQ и ожидание ответа.
        Создает уникальную временную очередь для каждого запроса.
        
        Args:
            payload (Dict[str, Any]): Данные для отправки
            queue_name (str): Имя очереди для отправки запроса
            
        Returns:
            Dict[str, Any]: Результат обработки запроса
        """
        # Генерируем уникальный correlation_id для этого запроса
        correlation_id = str(uuid.uuid4())

        self.logger.debug(
            f"🔍 [RABBITMQ] Отправка сообщения в очередь {queue_name}",
            extra={"correlation_id": correlation_id, "queue": queue_name},
        )
        self.logger.debug(f"🔍 [RABBITMQ] Payload keys: {list(payload.keys())}")
        self.logger.debug(f"🔍 [RABBITMQ] Correlation ID: {correlation_id}")

        # Создаем уникальную временную очередь для этого запроса
        callback_queue = await self.channel.declare_queue(
            exclusive=True, auto_delete=True
        )
        self.logger.debug(
            f"🔍 [RABBITMQ] Создана временная очередь: {callback_queue.name}"
        )

        # Регистрируем ожидание ответа
        self.pending_responses[correlation_id] = None

        # Настраиваем consumer для этой очереди
        async def on_message(message: aio_pika.IncomingMessage):
            await self._on_response(correlation_id, message)

        consumer_tag = await callback_queue.consume(on_message)
        self.logger.debug(
            f"🔍 [RABBITMQ] Consumer настроен для очереди {callback_queue.name}"
        )

        try:
            # Отправляем сообщение
            exchange = self.channel.default_exchange
            self.logger.debug(f"🔍 [RABBITMQ] Reply to: {callback_queue.name}")

            await exchange.publish(
                aio_pika.Message(
                    body=json.dumps(payload).encode(),
                    content_type="application/json",
                    correlation_id=correlation_id,
                    reply_to=callback_queue.name,
                ),
                routing_key=queue_name,
            )
            self.logger.debug("🔍 [RABBITMQ] Сообщение отправлено, ожидание ответа...")

            # Ждём ответа (с таймаутом)
            start_time = asyncio.get_event_loop().time()
            for i in range(6000):  # 600 секунд
                response = self.pending_responses.get(correlation_id)
                if response is not None:
                    elapsed = asyncio.get_event_loop().time() - start_time
                    result = json.loads(response)
                    self.logger.debug(
                        f"🔍 [RABBITMQ] ✅ Получен ответ за {elapsed:.2f}s",
                        extra={"correlation_id": correlation_id, "queue": queue_name},
                    )
                    self.logger.debug(
                        f"🔍 [RABBITMQ] Response keys: {list(result.keys())}"
                    )
                    return result

                # Логируем каждые 10 секунд
                if i % 100 == 0 and i > 0:
                    elapsed = asyncio.get_event_loop().time() - start_time
                    self.logger.debug(
                        f"🔍 [RABBITMQ] Ожидание ответа... ({elapsed:.1f}s)",
                        extra={"correlation_id": correlation_id, "queue": queue_name},
                    )

                await asyncio.sleep(0.1)

            self.logger.debug("🔍 [RABBITMQ] ❌ Таймаут после 600s")
            self.logger.error(
                "Превышено время ожидания ответа от воркера",
                extra={"correlation_id": correlation_id, "queue": queue_name},
            )
            raise TimeoutError(
                f"Таймаут ожидания ответа от воркера (queue: {queue_name})"
            )

        finally:
            # Очищаем ресурсы
            try:
                await callback_queue.cancel(consumer_tag)
                await callback_queue.delete()
                self.logger.debug(
                    f"🔍 [RABBITMQ] Очередь {callback_queue.name} удалена"
                )
            except Exception as e:
                self.logger.warning(f"🔍 [RABBITMQ] Ошибка при удалении очереди: {e}")

            # Удаляем из словаря ожидающих ответов
            self.pending_responses.pop(correlation_id, None)
    
    async def close(self):
        """
        Закрытие соединения с RabbitMQ.
        """
        try:
            self.logger.debug("🔍 [RABBITMQ] Закрытие соединения...")
            if self.connection and not self.connection.is_closed:
                await self.connection.close()
                self.logger.debug("🔍 [RABBITMQ] ✅ Соединение закрыто")
                self.logger.info("Соединение с RabbitMQ закрыто")
            else:
                self.logger.debug(
                    "🔍 [RABBITMQ] Соединение уже закрыто или не существует"
                )
        except Exception as e:
            self.logger.debug(
                f"🔍 [RABBITMQ] ❌ Ошибка при закрытии: {type(e).__name__}: {e}"
            )
            self.logger.error(f"Ошибка при закрытии соединения с RabbitMQ: {str(e)}")


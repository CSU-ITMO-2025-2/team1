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
        callback_queue: Очередь для получения ответов
        response: Хранит полученный ответ
        corr_id: Идентификатор корреляции для отслеживания запросов
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
        self.callback_queue = None
        self.response = None
        self.corr_id = None
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
        3. Объявление очереди обратного вызова
        4. Настройку обработчика ответов
        
        Raises:
            Exception: При ошибке подключения к RabbitMQ
        """
        try:
            self.logger.info("Подключение к RabbitMQ")
            self.connection = await aio_pika.connect_robust(
                self.rabbit_url,
                heartbeat=600  # 10 минут
            )
            self.channel = await self.connection.channel()

            self.logger.debug("Объявление очереди обратного вызова")
            self.callback_queue = await self.channel.declare_queue(exclusive=True)

            self.logger.debug("Настройка получателя сообщений")
            await self.callback_queue.consume(self.on_response)

            self.logger.info("Успешное подключение к RabbitMQ")
        except Exception as e:
            self.logger.error(f"Ошибка подключения к RabbitMQ: {str(e)}", exc_info=True)
            raise

    async def on_response(self, message: aio_pika.IncomingMessage):
        """
        Обработчик входящих сообщений.
        
        Args:
            message (aio_pika.IncomingMessage): Входящее сообщение от RabbitMQ
        """
        if self.corr_id == message.correlation_id:
            self.logger.debug(
                "Получено ответное сообщение",
                extra={"correlation_id": message.correlation_id}
            )
            self.response = message.body

    async def call(
        self, payload: Dict[str, Any], queue_name: str = "resume_evaluation_task"
    ) -> Dict[str, Any]:
        """
        Отправка RPC запроса в RabbitMQ и ожидание ответа.
        
        Args:
            payload (Dict[str, Any]): Данные для отправки
            queue_name (str): Имя очереди для отправки запроса
            
        Returns:
            Dict[str, Any]: Результат обработки запроса
        """
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.logger.debug(
            f"Отправка сообщения в очередь {queue_name}",
            extra={"correlation_id": self.corr_id}
        )

        exchange = self.channel.default_exchange
        await exchange.publish(
            aio_pika.Message(
                body=json.dumps(payload).encode(),
                content_type="application/json",
                correlation_id=self.corr_id,
                reply_to=self.callback_queue.name,
            ),
            routing_key=queue_name,  # Используем параметр очереди
        )

        # Ждём ответа (с таймаутом)
        self.logger.debug("Ожидание ответа")
        for _ in range(6000):  # 600 секунд
            if self.response is not None:
                result = json.loads(self.response)
                self.logger.debug(
                    "Получен ответ",
                    extra={"correlation_id": self.corr_id}
                )
                return result
            await asyncio.sleep(0.1)

        self.logger.error(
            "Превышено время ожидания ответа от воркера",
            extra={"correlation_id": self.corr_id}
        )
        raise TimeoutError("Таймаут ожидания ответа от воркера")
    
    async def close(self):
        """
        Закрытие соединения с RabbitMQ.
        """
        try:
            if self.connection and not self.connection.is_closed:
                await self.connection.close()
                self.logger.info("Соединение с RabbitMQ закрыто")
        except Exception as e:
            self.logger.error(f"Ошибка при закрытии соединения с RabbitMQ: {str(e)}")


"""
Воркер для обработки задач из RabbitMQ.
Вызывает run_pipeline из resume_evaluation_service.runner.
"""

import json
import os
import re

import pika
from dotenv import load_dotenv

from .runner import run_pipeline_sync
from .utils.logger import setup_logger

# Логирование
logger = setup_logger(__name__)

load_dotenv()

# Настройки RabbitMQ
RABBITMQ_USER = os.getenv("RABBITMQ_DEFAULT_USER")
RABBITMQ_PASS = os.getenv("RABBITMQ_DEFAULT_PASS")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT")
RABBITMQ_DEFAULT_VHOST = os.getenv("RABBITMQ_DEFAULT_VHOST")
RABBITMQ_DEFAULT_HOST = os.getenv("RABBITMQ_DEFAULT_HOST")
RABBITMQ_URL = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_DEFAULT_HOST}:{RABBITMQ_PORT}{RABBITMQ_DEFAULT_VHOST}"


def run_question_generation_worker():
    """
    Запускает воркер, слушающий очередь question_generation_task.
    При получении задачи вызывает runner.run_pipeline и отправляет результат.
    """
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()

    # Объявляем очередь
    channel.queue_declare(queue="question_generation_task", durable=True)
    channel.basic_qos(prefetch_count=1)

    def on_request(ch, method, properties, body):
        try:
            request_data = json.loads(body)
            vacancy_text = request_data.get("vacancy_text", None)
            resume_text = request_data.get("resume_text", None)
            report_raw = request_data.get("report")
            
            if report_raw.get("status") == "success":
                report = report_raw.get("data")
            else:
                logger.error("Не удалось получить отчет по образованию")
                return {"status": "failed"}

            print('report', report)

            # Выполняем пайплайн
            result = run_pipeline_sync(vacancy=vacancy_text, resume=resume_text, report=report)

            if result is None or result.get("status") == "failed":
                logger.error("Не удалось получить отчет по образованию")
                return {"status": "failed"}

            # Формируем ответ
            response = {
                "status": "success",
                "data": result,
            }

        except Exception as e:
            # Возвращаем валидный data даже при ошибке
            response = {
                "status": "error",
                "data": None,
                "message": f"Ошибка воркера: {str(e)}",
            }

        ch.basic_publish(
            exchange="",
            routing_key=properties.reply_to,
            properties=pika.BasicProperties(correlation_id=properties.correlation_id),
            body=json.dumps(response, ensure_ascii=False),
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info("💤 Готов к приёму новой задачи...")

    # Подключаем обработчик
    channel.basic_consume(
        queue="question_generation_task", on_message_callback=on_request
    )

    logger.info("✅ Воркер запущен. Ожидание задач...")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.info("🛑 Воркер остановлен")
        connection.close()


if __name__ == "__main__":
    run_question_generation_worker()

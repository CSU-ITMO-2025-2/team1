"""Сервис для генерации через RabbitMQ."""
from typing import Any, Dict
from app.logger import setup_logger

logger = setup_logger(__name__)


class GenerationService:
    """Сервис генерации контента через очереди RabbitMQ."""
    
    def __init__(self, rabbit_client):
        """
        Инициализация сервиса.
        
        Args:
            rabbit_client: Клиент RabbitMQ для отправки сообщений
        """
        self.rabbit_client = rabbit_client
    
    async def evaluate_resume(
        self,
        vacancy_text: str,
        resume_text: str
    ) -> Dict[str, Any]:
        """
        Оценить соответствие резюме вакансии.
        
        Args:
            vacancy_text: Текст вакансии
            resume_text: Текст резюме
            
        Returns:
            Dict[str, Any]: Результат оценки
        """
        logger.debug(
            "Отправка запроса на оценку резюме",
            extra={
                "vacancy_length": len(vacancy_text),
                "resume_length": len(resume_text)
            }
        )
        
        result = await self.rabbit_client.call(
            {"vacancy_text": vacancy_text, "resume_text": resume_text},
            queue_name="resume_evaluation_task"
        )
        
        logger.debug("Получен результат оценки резюме")
        return result
    
    async def generate_job_description(
        self,
        input_data: str
    ) -> Dict[str, Any]:
        """
        Сгенерировать описание вакансии.
        
        Args:
            input_data: Входные данные для генерации
            
        Returns:
            Dict[str, Any]: Сгенерированное описание вакансии
        """
        logger.debug(
            "Отправка запроса на генерацию описания вакансии",
            extra={"input_length": len(input_data)}
        )
        
        result = await self.rabbit_client.call(
            {"input_data": input_data},
            queue_name="job_description_task"
        )
        
        logger.debug("Получен результат генерации описания вакансии")
        return result
    
    async def generate_questions(
        self,
        vacancy_text: str,
        resume_text: str,
        evaluation_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Сгенерировать вопросы для интервью.
        
        Args:
            vacancy_text: Текст вакансии
            resume_text: Текст резюме
            evaluation_report: Результат оценки резюме
            
        Returns:
            Dict[str, Any]: Сгенерированные вопросы
        """
        logger.debug(
            "Отправка запроса на генерацию вопросов",
            extra={
                "vacancy_length": len(vacancy_text),
                "resume_length": len(resume_text)
            }
        )
        
        result = await self.rabbit_client.call(
            {
                "vacancy_text": vacancy_text,
                "resume_text": resume_text,
                "report": evaluation_report
            },
            queue_name="question_generation_task"
        )
        
        logger.debug("Получен результат генерации вопросов")
        return result


"""
Функция для извлечения данных о релевантности опыта с помощью LLM.
"""

from utils.clean_text import clean_text
from utils.logger import setup_logger
from pipelines.work_exp_evaluation.work_relevance_llm.work_relevance import evaluate_work_exp_relevance_llm

# Логирование
logger = setup_logger(__name__)


async def get_work_exp_relevance(response_work_exp, vacancy: str):
    """
    Асинхронно извлекает данные о релевантности опыта работы.

    Args:
        response_work_exp (dict): Результаты извлечения опыта работы
        vacancy (str): Текст вакансии

    Returns:
        Извлечённые данные или None при ошибке.
    """
    if not response_work_exp:
        logger.warning("Список опыта пуст — релевантность не может быть оценена")
        return {'status': 'failed'}

    if not vacancy or not vacancy.strip():
        logger.warning("Пустой текст вакансии — невозможно оценить релевантность опыта")
        return {'status': 'failed'}

    if not response_work_exp.get("work_list"):
        logger.warning(
            "response_work_exp.work_list пуст — пропускаем оценку релевантности опыта"
        )
        return {'status': 'failed'}

    # очищаем текст
    logger.info("Очищаем текст от лишних символов")
    cleaned_vacancy = clean_text(vacancy)
    logger.info("Текст очищен ")

    try:
        result = await evaluate_work_exp_relevance_llm(
            response_work_exp, vacancy=cleaned_vacancy
        )
        
        # Проверяем, что результат не None
        if result is None:
            logger.error("Результат равен None")
            return {'status': 'failed'}

        # Переводим в словарь
        result_dict = result.model_dump()

        # Устанавливаем флаг успешного выполнения
        result_dict['status'] = 'success'
        return result_dict
        
    except Exception as e:
        logger.error(f"Ошибка выполнения: {str(e)}", exc_info=True)
        return {'status': 'failed'}

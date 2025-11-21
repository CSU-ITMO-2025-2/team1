"""
Функция-обертка, которая обрабатывает входной текст и запускает процесс матчинга cкиллов из резюме.
"""

from ...utils.logger import setup_logger
from .skills_match_llm.skills_match import skills_match_llm

# Логирование
logger = setup_logger(__name__)


async def get_skills_match(vacancy_skills: list, agg_skills: list):
    """
    Асинхронно матчит навыки

    Args:
        vacancy_skills (list): Список требуемых навыков в вакансии
        agg_skills (list): Список агрегированных навыков из резюме

    Returns:
        Извлечённые данные или None при ошибке.
    """
    
    # Проверяем, что список скилов не пустой и не состоит только из пробелов
    if not vacancy_skills or all(skill.strip() == '' for skill in vacancy_skills):
        logger.warning("Пустой список для очистки скилов")
        return {'status': 'failed'}
    
    # Проверяем, что список скилов не пустой и не состоит только из пробелов
    if not agg_skills or all(skill.strip() == '' for skill in agg_skills):
        logger.warning("Пустой список для очистки скилов")
        return {'status': 'failed'}

    try:
        result = await skills_match_llm(vacancy_skills, agg_skills)
        # Проверяем, что результат не None
        if result is None:
            logger.error("Результат равен None")
            return {'status': 'failed'}
        
        # Переводим в словарь
        result_dict = result.model_dump()

        # Устанавливаем флаг успешного выполнения
        result_dict['status'] = 'success'
        logger.info("Успешное выполнение матчинга навыков")
        return result_dict
        
    except Exception as e:
        logger.error(f"Ошибка выполнения: {str(e)}", exc_info=True)
        return {'status': 'failed'}

from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.prompts.few_shot import FewShotChatMessagePromptTemplate

from pipelines.education_evaluation.prompts.extract_courses.examples import course_extraction_examples
from pipelines.education_evaluation.prompts.extract_courses.human import human_courses_extraction as human
from pipelines.education_evaluation.prompts.extract_courses.system import system_course_extraction_prompt as system

# Оборачиваем системный промпт
extract_course_system_prompt = SystemMessagePromptTemplate.from_template(
    system
)

# Оборачиваем примеры
example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{input}"),
        ("ai", "{output}"),
    ]
)

extract_course_edu_examples = FewShotChatMessagePromptTemplate(
    examples=course_extraction_examples, example_prompt=example_prompt
)

# оборачиваем хьюман промпт
extract_course_human_prompt = HumanMessagePromptTemplate.from_template(human)

# Собираем промпт в шаблон
extract_course_full_prompt = ChatPromptTemplate.from_messages(
    [
        extract_course_system_prompt,
        extract_course_edu_examples,
        extract_course_human_prompt,
    ]
)

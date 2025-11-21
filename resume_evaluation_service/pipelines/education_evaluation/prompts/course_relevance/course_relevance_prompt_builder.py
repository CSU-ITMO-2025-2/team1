import sys
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.prompts.few_shot import FewShotChatMessagePromptTemplate

from .examples import relevance_examples
from .human import course_relevance_human_prompt as human
from .system import system_relevance_course_prompt as system

# Оборачиваем системный промпт
relevance_course_system_prompt = SystemMessagePromptTemplate.from_template(
    system
)

# Оборачиваем примеры
example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{input}"),
        ("ai", "{output}"),
    ]
)

relevance_course_edu_examples = FewShotChatMessagePromptTemplate(
    examples=relevance_examples, example_prompt=example_prompt
)

# оборачиваем хьюман промпт
relevance_course_human_prompt = HumanMessagePromptTemplate.from_template(human)

# Собираем промпт в шаблон
relevance_course_full_prompt = ChatPromptTemplate.from_messages(
    [
        relevance_course_system_prompt,
        relevance_course_edu_examples,
        relevance_course_human_prompt,
    ]
)

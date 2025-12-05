from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.prompts.few_shot import FewShotChatMessagePromptTemplate

from pipelines.job_description.prompts.soft_skills.examples import soft_skills_examples
from pipelines.job_description.prompts.soft_skills.human_prompt import human_prompt_soft_skills as human
from pipelines.job_description.prompts.soft_skills.system_prompt import system_soft_skills_prompt

# Оборачиваем системный промпт
system_prompt = SystemMessagePromptTemplate.from_template(system_soft_skills_prompt)

# Оборачиваем примеры
example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{input}"),
        ("ai", "{output}"),
    ]
)

# Оформляем примеры
examples = FewShotChatMessagePromptTemplate(
    examples=soft_skills_examples, example_prompt=example_prompt
)

# оборачиваем хьюман промпт
human_prompt = HumanMessagePromptTemplate.from_template(human)

# Собираем промпт в шаблон
soft_skills_full_prompt = ChatPromptTemplate.from_messages(
    [
        system_prompt,
        examples,
        human_prompt,
    ]
)

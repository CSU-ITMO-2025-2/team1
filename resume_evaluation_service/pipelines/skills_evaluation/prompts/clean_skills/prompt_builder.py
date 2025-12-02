from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.prompts.few_shot import FewShotChatMessagePromptTemplate

from pipelines.skills_evaluation.prompts.clean_skills.examples import skill_classification_examples
from pipelines.skills_evaluation.prompts.clean_skills.human import skills_classification_human_prompt as human
from pipelines.skills_evaluation.prompts.clean_skills.system import skill_classification_system_prompt as system

# Оборачиваем системный промпт
system_prompt = SystemMessagePromptTemplate.from_template(
    system
)

# Оборачиваем примеры
example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{input}"),
        ("ai", "{output}"),
    ]
)

examples = FewShotChatMessagePromptTemplate(
    examples=skill_classification_examples, example_prompt=example_prompt
)

# оборачиваем хьюман промпт
human_prompt = HumanMessagePromptTemplate.from_template(human)

# Собираем промпт в шаблон
clean_skills_full_prompt = ChatPromptTemplate.from_messages(
    [
        system_prompt,
        examples,
        human_prompt,
    ]
)

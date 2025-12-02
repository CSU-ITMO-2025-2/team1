from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.prompts.few_shot import FewShotChatMessagePromptTemplate

from pipelines.skills_evaluation.prompts.classify_skills.examples import examples_vac_skills
from pipelines.skills_evaluation.prompts.classify_skills.human import human
from pipelines.skills_evaluation.prompts.classify_skills.system import system_prompt_vac_skills

# Оборачиваем системный промпт
system_prompt = SystemMessagePromptTemplate.from_template(system_prompt_vac_skills)

# Оборачиваем примеры
example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{input}"),
        ("ai", "{output}"),
    ]
)

examples = FewShotChatMessagePromptTemplate(
    examples=examples_vac_skills, example_prompt=example_prompt
)

# оборачиваем хьюман промпт
human_prompt = HumanMessagePromptTemplate.from_template(human)

# Собираем промпт в шаблон
classify_skills_full_prompt = ChatPromptTemplate.from_messages(
    [
        system_prompt,
        examples,
        human_prompt,
    ]
)

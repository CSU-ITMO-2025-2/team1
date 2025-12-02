from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.prompts.few_shot import FewShotChatMessagePromptTemplate

from pipelines.format_job_description.prompts.flyer.examples import flyer_examples
from pipelines.format_job_description.prompts.flyer.human_prompt import human_flyer_prompt as human
from pipelines.format_job_description.prompts.flyer.system_prompt import system_flyer_prompt as system

# Оборачиваем системный промпт
system_prompt = SystemMessagePromptTemplate.from_template(system)

# Оборачиваем примеры
example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{input}"),
        ("ai", "{output}"),
    ]
)

# Оборачиваем примеры
examples = FewShotChatMessagePromptTemplate(
    examples=flyer_examples, example_prompt=example_prompt
)

# оборачиваем хьюман промпт
human_prompt = HumanMessagePromptTemplate.from_template(human)

# Собираем промпт в шаблон
flyer_full_prompt = ChatPromptTemplate.from_messages(
    [
        system_prompt,
        examples,
        human_prompt,
    ]
)

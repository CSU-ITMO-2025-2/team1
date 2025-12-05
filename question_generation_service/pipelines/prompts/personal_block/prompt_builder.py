from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.prompts.few_shot import FewShotChatMessagePromptTemplate

from pipelines.prompts.personal_block.examples import personal_block_examples as examples
from pipelines.prompts.personal_block.human import personal_block_human_prompt as human
from pipelines.prompts.personal_block.system import personal_block_system_prompt as system

# Оборачиваем системный промпт
system_prompt = SystemMessagePromptTemplate.from_template(system)

# Оборачиваем примеры
example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{input}"),
        ("ai", "{output}"),
    ]
)

# Оформляем примеры
prepared_examples = FewShotChatMessagePromptTemplate(
    examples=examples, example_prompt=example_prompt
)

# оборачиваем хьюман промпт
human_prompt = HumanMessagePromptTemplate.from_template(human)

# Собираем промпт в шаблон
personal_block_full_prompt = ChatPromptTemplate.from_messages(
    [
        system_prompt,
        prepared_examples,
        human_prompt,
    ]
)

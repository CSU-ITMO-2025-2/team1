from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.prompts.few_shot import FewShotChatMessagePromptTemplate

from pipelines.prompts.experience_block.examples import experience_block_examples as examples
from pipelines.prompts.experience_block.human import experience_block_human_prompt as human
from pipelines.prompts.experience_block.system import experience_block_system_prompt as system

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
experience_block_full_prompt = ChatPromptTemplate.from_messages(
    [
        system_prompt,
        prepared_examples,
        human_prompt,
    ]
)

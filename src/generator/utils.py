from typing import Iterator
from itertools import zip_longest
from llm_sdk.llm_sdk import Small_LLM_Model
from ..parser import FuncDefData
from .models import Func


class Utils:
    @staticmethod
    def tokenize_functions(
        model: Small_LLM_Model,
        func_names: list[str]
    ) -> list[list[int]]:
        tokenized_funcs: list[list[int]] = []

        for func in func_names:
            func = func.replace('_', ' ')
            tokenized_funcs.append(model.encode(func).tolist()[0][1:])

        return tokenized_funcs

    @staticmethod
    def restrict_logits(logits: list[float], allowed_tokens: set[int]) -> list[float]:
        for token_id in range(len(logits)):
            if token_id not in allowed_tokens:
                logits[token_id] = float('-inf')

        return logits

    @staticmethod
    def update_allowed_funcs(
        allowed_funcs: list[list[int]]
    ) -> Iterator[list[int]]:
        for tokens in zip_longest(*allowed_funcs, fillvalue=None):
            yield [token for token in tokens if token is not None]

    @staticmethod
    def format_prompts(prompts: list[str]) -> list[str]:
        return [
            prompt.lower().rstrip('.').strip()
            for prompt in prompts
        ]

    @staticmethod
    def exclude_tokens(tokens: list[int], answer: list[int]) -> list[int]:
        for token in tokens:
            if token in answer:
                tokens.remove(token)

        return tokens

    @staticmethod
    def get_highest_average(
        logits: list[float],
        token_groups: list[list[int]],
    ) -> list[int]:
        averages: list[float] = []
        for func in token_groups:
            averages.append(sum([logits[t] for t in func]) / len(func))

        return token_groups[averages.index(max(averages))]

    @staticmethod
    def build_func_context(functions: list[FuncDefData]) -> str:
        context: str = 'These are your functions. Only one must be chosen at a '
        context += 'time. Choose the best one for each task.\n'
        for function in functions:
            context += 'function name: ' + function.name.replace('fn_', '') + '\n'
            context += 'description: ' + function.description + '\n\n'

        return context

    @staticmethod
    def build_param_context(chosen_func: FuncDefData) -> str:
        context: str = chosen_func.name + ':\n'
        context += 'description: ' + chosen_func.description + '\n'
        context += 'parameters:\n'
        for name, type in chosen_func.parameters.items():
            context += '\t' + name + ': ' + type.type + '\n'

        return context

    @staticmethod
    def write_json_output(
        functions: list[Func],
        output_file_path: str
    ) -> None:
        file_content: str = '[\n'

        for func in functions:
            file_content += '\t{\n'
            file_content += f'\t\t"prompt": "{func.prompt.replace('"', '\\"')}",\n'
            file_content += f'\t\t"name": "{func.name}",\n'
            file_content += '\t\t"parameters": {' + ', '.join(
                [
                    f'"{name}": ' + (val if val.isnumeric() else f'"{val}"')
                    for name, val in func.params.items()
                ]
            ) + '}\n'
            file_content += '\t},'
        file_content = file_content[:-1]
        file_content += ']'

        with open(output_file_path, 'w') as out_file:
            out_file.write(file_content)

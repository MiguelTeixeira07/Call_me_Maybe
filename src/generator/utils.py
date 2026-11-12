from typing import Iterator
from itertools import zip_longest
from llm_sdk.llm_sdk import Small_LLM_Model


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
    def choose_function(
        logits: list[float],
        functions: list[list[int]],
    ) -> list[int]:
        averages: list[float] = []
        for func in functions:
            averages.append(sum([logits[t] for t in func]) / len(func))

        return functions[averages.index(max(averages))]

from llm_sdk.llm_sdk import Small_LLM_Model


class Utils:
    @staticmethod
    def tokenize_functions(
        model: Small_LLM_Model,
        func_names: list[str]
    ) -> dict[str, list[int]]:
        tokenized_funcs: dict[str, list[int]] = {}

        for func in func_names:
            tokenized_funcs.update({func: model.encode(func).tolist()[0]})

        return tokenized_funcs

    @staticmethod
    def restrict_logits(logits: list[float], allowed_tokens: set[int]) -> list[float]:
        for token_id in range(len(logits)):
            if token_id not in allowed_tokens:
                logits[token_id] = float('-inf')

        return logits

    @staticmethod
    def update_allowed_funcs(
        allowed_funcs: dict[str, list[int]],
        generated
    ) -> dict[str, list[int]]:
        current = allowed_funcs

        for token in generated:
            if token not in current:
                return {}
            current = current[token]

        return {
            token: child
            for token, child in current.items()
            if token is not None
        }

from typing import Iterator
from itertools import zip_longest
from llm_sdk.llm_sdk import Small_LLM_Model
from ..parser import FuncDefData
from .models import Func


class Utils:
    """Helper functions for the function-calling pipeline.

    Groups the static methods used to build prompts, constrain the model's
    logits, generate parameter values and write the final JSON output.
    """
    @staticmethod
    def tokenize_functions(
        model: Small_LLM_Model,
        func_names: list[str]
    ) -> list[list[int]]:
        """Tokenizes function names.

        Underscores are replaced with spaces before encoding, and the first
        token of each encoding is dropped.

        Args:
            model (Small_LLM_Model): Model whose tokenizer is used.
            func_names (list[str]): Function names to tokenize.

        Returns:
            list[list[int]]: Token ids of each function name, in the same
                order as func_names.
        """
        tokenized_funcs: list[list[int]] = []

        for func in func_names:
            func = func.replace('_', ' ')
            tokenized_funcs.append(model.encode(func).tolist()[0][1:])

        return tokenized_funcs

    @staticmethod
    def restrict_logits(
        logits: list[float],
        allowed_tokens: set[int]
    ) -> list[float]:
        """Restricts the logits to a set of allowed tokens.

        The logit of every token that is not allowed is set to negative
        infinity, so it can never be selected. The list is modified in place.

        Args:
            logits (list[float]): Logits for every token in the vocabulary.
            allowed_tokens (set[int]): Token ids that may still be selected.

        Returns:
            list[float]: The same logits list with disallowed tokens masked.
        """
        for token_id in range(len(logits)):
            if token_id not in allowed_tokens:
                logits[token_id] = float('-inf')

        return logits

    @staticmethod
    def update_allowed_funcs(
        allowed_funcs: list[list[int]]
    ) -> Iterator[list[int]]:
        """Yields the allowed tokens for each generation step.

        At step i, yields the i-th token of every function whose token list
        is long enough, skipping the ones that have already ended.

        Args:
            allowed_funcs (list[list[int]]): Token ids of each candidate
                function.

        Yields:
            list[int]: Tokens allowed at the current position.
        """
        for tokens in zip_longest(*allowed_funcs, fillvalue=None):
            yield [token for token in tokens if token is not None]

    @staticmethod
    def format_prompts(prompts: list[str]) -> list[str]:
        """Normalizes prompts.

        Converts each prompt to lowercase and removes surrounding whitespace
        and trailing periods.

        Args:
            prompts (list[str]): Raw prompts.

        Returns:
            list[str]: Formatted prompts.
        """
        return [
            prompt.lower().rstrip('.').strip()
            for prompt in prompts
        ]

    @staticmethod
    def exclude_tokens(tokens: list[int], answer: list[int]) -> list[int]:
        """Removes from tokens those that already appear in the answer.

        The tokens list is modified in place.

        Args:
            tokens (list[int]): Candidate token ids.
            answer (list[int]): Token ids generated so far.

        Returns:
            list[int]: The same tokens list after removal.
        """
        for token in tokens:
            if token in answer:
                tokens.remove(token)

        return tokens

    @staticmethod
    def get_highest_average(
        logits: list[float],
        token_groups: list[list[int]],
    ) -> list[int]:
        """Finds the token group with the highest average logit.

        Args:
            logits (list[float]): Logits for every token in the vocabulary.
            token_groups (list[list[int]]): Groups of token ids, such as the
                tokens of each function name.

        Returns:
            list[int]: The token group with the highest average logit.
        """
        averages: list[float] = []
        for func in token_groups:
            averages.append(sum([logits[t] for t in func]) / len(func))

        return token_groups[averages.index(max(averages))]

    @staticmethod
    def build_func_context(functions: list[FuncDefData]) -> str:
        """Builds the prompt context used to choose a function.

        Lists the name (without the "fn_" prefix) and description of every
        function, preceded by instructions for the model.

        Args:
            functions (list[FuncDefData]): Definitions of all available
                functions.

        Returns:
            str: Context text describing the available functions.
        """
        context: str = \
            'These are your functions. Only one must be chosen at a '
        context += 'time. Choose the best one for each task.\n'
        for function in functions:
            context += 'function name: ' + \
                function.name.replace('fn_', '') + '\n'
            context += 'description: ' + function.description + '\n\n'

        return context

    @staticmethod
    def build_param_context(chosen_func: FuncDefData) -> str:
        """Builds the prompt context used to generate parameter values.

        Describes the chosen function with its name, description and the
        type of each parameter.

        Args:
            chosen_func (FuncDefData): Definition of the chosen function.

        Returns:
            str: Context text describing the function and its parameters.
        """
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
        """Writes the function call results to a JSON file.

        Numeric parameter values are written as numbers and all other values
        as strings.

        Args:
            functions (list[Func]): Results to write.
            output_file_path (str): Path of the output file.
        """
        file_content: str = '['

        for func in functions:
            file_content += '\n\t{\n'
            file_content += '\t\t"prompt": "' + \
                func.prompt.replace('"', '\\"') + '",\n'
            file_content += f'\t\t"name": "{func.name}",\n'
            file_content += '\t\t"parameters": {' + ', '.join(
                [
                    f'"{name}": ' +
                    (str(val) if isinstance(val, float) else f'"{val}"')
                    for name, val in func.params.items()
                ]
            ) + '}\n'
            file_content += '\t},'
        file_content = file_content[:-1]
        file_content += '\n]'

        with open(output_file_path, 'w') as out_file:
            out_file.write(file_content)

    @staticmethod
    def generate_param(
        param: str,
        type: str,
        input_ids: list[int],
        model: Small_LLM_Model
    ) -> tuple[list[int], list[int]]:
        """Generates the value of a single parameter.

        Appends a follow-up question to the input and generates tokens
        greedily until a closing double quote is produced. For parameters of
        type 'number', the logits are restricted to digits and the quote.

        Args:
            param (str): Name of the parameter to generate.
            type (str): Type of the parameter ('number' or 'string').
            input_ids (list[int]): Token ids of the context so far. Extended
                in place.
            model (Small_LLM_Model): Model used to generate the tokens.

        Returns:
            tuple[list[int], list[int]]: The generated token ids and the
                updated input ids.
        """
        follow_up: str = f'\nThe best value for parameter "{param}" is "'
        input_ids += model.encode(follow_up).tolist()[0]

        logits: list[float] = []
        answer: list[int] = []
        while '"' not in model.decode(answer):
            if type == 'number':
                logits = Utils.restrict_logits(
                    model.get_logits_from_input_ids(input_ids),
                    set(model.encode('0123456789"').tolist()[0])
                )
            else:
                logits = model.get_logits_from_input_ids(
                    input_ids
                )
            input_ids.append(logits.index(max(logits)))
            answer.append(logits.index(max(logits)))

        return (answer, input_ids)

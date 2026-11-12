from llm_sdk.llm_sdk import Small_LLM_Model
from .utils import Utils
from ..parser import FuncDefData


class LLM:
    @staticmethod
    def main(functions: list[FuncDefData], prompts: list[str]) -> None:
        func_names = [func.name for func in functions]

        model: Small_LLM_Model = Small_LLM_Model()

        tokenized_funcs: list[list[int]] = Utils.tokenize_functions(
            model,
            func_names
        )

        context: str = 'These are your functions. Only one must be chosen at a '
        context += 'time. Choose the best one for each task.\n'
        for function in functions:
            context += 'function name: ' + function.name.replace('fn_', '') + '\n'
            context += 'description: ' + function.description + '\n\n'

        follow_up: str = ' The name of the best function to do this is '

        prompts = Utils.format_prompts(prompts)

        for prompt in prompts:
            input_ids: list[int] = model.encode(
                context +
                prompt +
                follow_up
            ).tolist()[0]

            logits: list[float] = Utils.restrict_logits(
                model.get_logits_from_input_ids(input_ids),
                {token for func in tokenized_funcs for token in func}
            )

            answer = Utils.choose_function(logits, tokenized_funcs)

            print(prompt)
            print('fn' + model.decode(answer).replace(' ', '_'))
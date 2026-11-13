from llm_sdk.llm_sdk import Small_LLM_Model
from .utils import Utils
from .models import Func
from ..parser import FuncDefData


class FunctionCaller:
    @staticmethod
    def run(functions: list[FuncDefData], prompts: list[str]) -> None:
        model: Small_LLM_Model = Small_LLM_Model()

        prompts = Utils.format_prompts(prompts)

        chosen_funcs: list[str] = FunctionCaller.get_chosen_functions(
            prompts,
            model,
            functions
        )

        funcs: list[Func] = FunctionCaller.get_prompts(
            functions,
            chosen_funcs,
            prompts,
            model
        )

        return funcs

    @staticmethod
    def get_chosen_functions(
        prompts: list[str],
        model: Small_LLM_Model,
        functions: list[FuncDefData]
    ) -> list[str]:
        context: str = Utils.build_func_context(functions)
        follow_up: str = ' The name of the best function to do this is '
        answers: list[str] = []
        tokenized_funcs: list[list[int]] = Utils.tokenize_functions(
            model,
            [func.name for func in functions]
        )

        for prompt in prompts:
            prompt = context + prompt + follow_up
            input_ids: list[int] = model.encode(prompt).tolist()[0]

            logits: list[float] = Utils.restrict_logits(
                model.get_logits_from_input_ids(input_ids),
                {token for func in tokenized_funcs for token in func}
            )

            answers.append(
                'fn' +
                model.decode(
                    Utils.get_highest_average(
                        logits,
                        tokenized_funcs
                    )
                ).replace(' ', '_')
            )

        return answers

    @staticmethod
    def get_prompts(
        functions: list[FuncDefData],
        chosen_funcs: list[str],
        prompts: list[str],
        model: Small_LLM_Model
    ) -> list[Func]:
        output: list[Func] = []

        for func_name, prompt in zip(chosen_funcs, prompts):
            chosen_func: FuncDefData = next(
                func for func in functions if func_name == func.name
            )
            context: str = Utils.build_param_context(chosen_func)
            input_ids: list[float] = model.encode(
                context +
                prompt
            ).tolist()[0]
            answers: list[str] = []
            for param, type in chosen_func.parameters.items():
                follow_up: str = f'\nThe best value for parameter "{param}" is "'
                input_ids += model.encode(follow_up).tolist()[0]

                answer: list[int] = []
                while '"' not in model.decode(answer):
                    if type.type == 'number':
                        logits: list[float] = Utils.restrict_logits(
                            model.get_logits_from_input_ids(input_ids),
                            model.encode('0123456789"')
                        )
                    else:
                        logits: list[float] = model.get_logits_from_input_ids(
                            input_ids
                        )
                    input_ids.append(logits.index(max(logits)))
                    answer.append(logits.index(max(logits)))

                answers.append(model.decode(answer))

            output.append(Func(
                prompt=prompt,
                name=chosen_func.name,
                params={name: ans[:ans.index('"')] for name, ans in zip(
                    chosen_func.parameters.keys(),
                    answers
                )}
            ))

        return output
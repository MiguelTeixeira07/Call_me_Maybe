from llm_sdk.llm_sdk import Small_LLM_Model
from .utils import Utils
from .models import Func
from ..parser import FuncDefData


class FunctionCaller:
    """Function caller driven by a small LLM.

    Uses constrained decoding to pick the best function for each prompt and to
    generate the value of each of that function's parameters.
    """
    @staticmethod
    def run(functions: list[FuncDefData], prompts: list[str]) -> list[Func]:
        """Runs the full function-calling pipeline.

        Formats the prompts, chooses a function for each one and then
        generates the parameter values for every chosen function.

        Args:
            functions (list[FuncDefData]): Definitions of all available
                functions.
            prompts (list[str]): Raw prompts to process.

        Returns:
            list[Func]: One result per prompt, containing the prompt, the
                chosen function name and the generated parameters.
        """
        model: Small_LLM_Model = Small_LLM_Model()

        unformatted_prompts: str = prompts
        prompts = Utils.format_prompts(prompts)

        print("=== Generating Functions ===\n")
        chosen_funcs: list[str] = FunctionCaller.get_chosen_functions(
            prompts,
            model,
            functions
        )

        print("=== Generating Parameters ===\n")
        funcs: list[Func] = FunctionCaller.get_params(
            functions,
            chosen_funcs,
            prompts,
            model,
            unformatted_prompts
        )

        return funcs

    @staticmethod
    def get_chosen_functions(
        prompts: list[str],
        model: Small_LLM_Model,
        functions: list[FuncDefData]
    ) -> list[str]:
        """Chooses the best function for each prompt.

        Builds a context describing all functions, restricts the model's
        logits to the tokens of the function names and selects the function
        whose tokens have the highest average logit.

        Args:
            prompts (list[str]): Formatted prompts to choose functions for.
            model (Small_LLM_Model): Model used to compute the logits.
            functions (list[FuncDefData]): Definitions of all available
                functions.

        Returns:
            list[str]: Name of the chosen function for each prompt, in the
                same order as the prompts.
        """
        context: str = Utils.build_func_context(functions)
        follow_up: str = ' The name of the best function to do this is '
        answers: list[str] = []
        tokenized_funcs: list[list[int]] = Utils.tokenize_functions(
            model,
            [func.name for func in functions]
        )

        for prompt in prompts:
            print(f'prompt: "{prompt}"')

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
            print(f'Chosen function: "{answers[-1]}"\n')

        return answers

    @staticmethod
    def get_params(
        functions: list[FuncDefData],
        chosen_funcs: list[str],
        prompts: list[str],
        model: Small_LLM_Model,
        unformatted_prompts: list[str]
    ) -> list[Func]:
        """Generates the parameter values for every chosen function.

        For each prompt, builds a context from the chosen function's
        definition and generates its parameters one at a time.

        Args:
            functions (list[FuncDefData]): Definitions of all available
                functions.
            chosen_funcs (list[str]): Chosen function name for each prompt.
            prompts (list[str]): Formatted prompts, aligned with
                chosen_funcs.
            model (Small_LLM_Model): Model used to generate the values.

        Returns:
            list[Func]: One result per prompt with the function name and the
                generated parameter values.
        """
        output: list[Func] = []
        answers: list[str] = []
        context: str = ''
        ans: str
        input_ids: list[int] = []

        for func_name, prompt, u_prompt in zip(
            chosen_funcs,
            prompts,
            unformatted_prompts
        ):
            chosen_func: FuncDefData = next(
                func for func in functions if func_name == func.name
            )
            if any(
                t.type == 'string' for t in chosen_func.parameters.values()
            ):
                prompt = u_prompt

            print(f'Prompt: "{prompt}"')
            print(f'Function: "{func_name}"')

            context = Utils.build_param_context(chosen_func)
            input_ids = model.encode(
                context +
                prompt
            ).tolist()[0]
            answers = []
            for param, type in chosen_func.parameters.items():
                answer, input_ids = Utils.generate_param(
                    param,
                    type.type,
                    input_ids,
                    model
                )
                ans = model.decode(answer)
                ans = ans[:ans.index('"')]
                answers.append(ans)

                print(f'\tParam "{param}": "{ans}"')

            output.append(Func(
                prompt=u_prompt,
                name=chosen_func.name,
                params={name: a for name, a in zip(
                    chosen_func.parameters.keys(),
                    answers
                )}
            ))
            print()

        return output

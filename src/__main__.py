from .parser import *
from .utils import Utils
from llm_sdk.llm_sdk import Small_LLM_Model


def main() -> None:
    argParser: ArgumentParser = ArgumentParser()
    args: Args = argParser.get_args()

    functionParser: FuncDefParser = FuncDefParser(filename=args.func_def_file)
    promptParser: InputFileParser = InputFileParser(filename=args.input_file)

    functionParser.validate_file()
    functions: list[FuncDefData] = functionParser.get_data()

    promptParser.validate_file()
    prompts: list[str] = promptParser.get_data()

    model: Small_LLM_Model = Small_LLM_Model()

    tokenized_funcs: dict[str, list[int]] = Utils.tokenize_functions(
        model,
        [func.name for func in functions]
    )

    for prompt in prompts:
        allowed_funcs: dict[str, list[int]] = tokenized_funcs
        input_ids: list[int] = model.encode(prompt).tolist()[0]
        input_ids_length: int = len(input_ids)

        #while len(allowed_funcs) > 1:
        while not model.decode(input_ids).endswith('!'):
            logits = Utils.restrict_logits(
                model.get_logits_from_input_ids(input_ids),
                {token for val in allowed_funcs.values() for token in val}
            )

            next_token = logits.index(max(logits))

            input_ids.append(next_token)

            allowed_funcs = Utils.update_allowed_funcs(
                allowed_funcs,
                input_ids[input_ids_length:]
            )

        print(prompt)
        print(model.decode(input_ids[input_ids_length:]))


if __name__ == '__main__':
    #try:
    main()
    #except BaseException as e:
        #print(e)

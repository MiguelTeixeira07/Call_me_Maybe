from .parser import *
from .generator import *
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

    generator: LLM = LLM()

    generator.main(functions, prompts)


if __name__ == '__main__':
    #try:
    main()
    #except BaseException as e:
        #print(e)

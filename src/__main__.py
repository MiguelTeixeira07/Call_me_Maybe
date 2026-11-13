from .parser import (
    ArgumentParser,
    InputFileParser,
    FuncDefData,
    FuncDefParser,
    Args
)
from .generator import Func, FunctionCaller, Utils


def main() -> None:
    argParser: ArgumentParser = ArgumentParser()
    args: Args = argParser.get_args()

    functionParser: FuncDefParser = FuncDefParser(filename=args.func_def_file)
    promptParser: InputFileParser = InputFileParser(filename=args.input_file)

    functionParser.validate_file()
    functions: list[FuncDefData] = functionParser.get_data()

    promptParser.validate_file()
    prompts: list[str] = promptParser.get_data()

    output_content: list[Func] = FunctionCaller.run(functions, prompts)

    Utils.write_json_output(output_content, args.output_file)


if __name__ == '__main__':
    #try:
    main()
    #except BaseException as e:
        #print(e)

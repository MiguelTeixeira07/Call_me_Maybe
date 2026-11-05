from .parser import *


def main() -> None:
    argParser: ArgumentParser = ArgumentParser()
    args: Args = argParser.get_args()

    print(
        args.func_def_file,
        args.input_file,
        args.output_file,
        sep='\n'
    )
    print()
    functionParser: FuncDefParser = FuncDefParser(filename=args.func_def_file)
    promptParser: InputFileParser = InputFileParser(filename=args.input_file)

    functionParser.validate_file()
    functions: list[FuncDefData] = functionParser.get_data()
    print('\n'.join([f'{func.name} | {func.description} | {func.parameters} | {func.returns.type}' for func in functions]))
    print()
    promptParser.validate_file()
    prompts: list[str] = promptParser.get_data()
    print('\n'.join([prompt for prompt in prompts]))


if __name__ == '__main__':
    #try:
    main()
    #except BaseException as e:
        #print(e)

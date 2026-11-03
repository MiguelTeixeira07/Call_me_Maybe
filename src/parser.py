import argparse
import sys
from typing import Any
from pydantic import BaseModel, model_validator
from colorama import Fore


class ParsingError(Exception):
    def __init__(self, msg) -> None:
        super().__init__(msg)


class Args(BaseModel):
    func_def_file: str
    input_file: str
    output_file: str

    @model_validator(mode='after')
    def validator(self) -> 'Args':
        if any(s for s in [
            self.func_def_file,
            self.output_file,
            self.input_file
        ] if len(s) > 4 and not s.endswith('.json')):
            raise ParsingError('All input files must be json files')

        return self


class Parser:
    def __init__(self) -> None:
        parser = argparse.ArgumentParser(
            usage='uv run python -m src [--functions_definition '
            '<function_definition_file>] [--input <input_file>] '
            '[--output <output_file>]',
            exit_on_error=False)

        parser.add_argument(
            '--functions_definition',
            type=str,
            required=True,
            help='function definition file'
        )
        parser.add_argument(
            '--input',
            type=str,
            required=True,
            help='input file'
        )
        parser.add_argument(
            '--output',
            type=str,
            required=True,
            help='output file'
        )

        try:
            args: Any = parser.parse_args()
            self.args: Args = Args(
                func_def_file=args.functions_definition,
                input_file=args.input,
                output_file=args.output
            )
        except ParsingError as e:
            print(Fore.RED + 'Error:' + Fore.RESET, e)
            sys.exit()
        except argparse.ArgumentError as e:
            parser.print_usage()
            print(e)
            sys.exit()

import sys
import json
import jsonschema
from argparse import ArgumentParser as ArgParser, ArgumentError
from typing import Any
from pydantic import BaseModel, ConfigDict, Field
from abc import ABC, abstractmethod
from .exceptions import ParsingError, SchemaError
from .models import Args, FuncDefData


class ArgumentParser:
    """Argument Parser.

    Uses argparse to validate and parse all the required arguments.

    Attributes:
        parser (argparse.ArgumentParser): argparse's argument parser object
    """
    def __init__(self) -> None:
        """Initializes argparse's ArgumentParser and adds required arguments"""
        self.parser: ArgParser = ArgParser(
            usage='uv run python -m src [--functions_definition '
            '<function_definition_file>] [--input <input_file>] '
            '[--output <output_file>]',
            exit_on_error=False)

        self.parser.add_argument(
            '--functions_definition',
            type=str,
            required=True,
            help='function definition file'
        )
        self.parser.add_argument(
            '--input',
            type=str,
            required=True,
            help='input file'
        )
        self.parser.add_argument(
            '--output',
            type=str,
            required=True,
            help='output file'
        )

    def get_args(self) -> Args:
        """Exports the data parsed from the command-line arguments

        Returns:
            Args: Parsed data
        """
        try:
            args: Any = self.parser.parse_args()
            return Args(
                func_def_file=args.functions_definition,
                input_file=args.input,
                output_file=args.output
            )
        except ParsingError as e:
            print(e)
            sys.exit()
        except ArgumentError as e:
            self.parser.print_usage()
            print(e)
            sys.exit()


class JsonParser(BaseModel, ABC):
    """Abstract parser for JSON files.

    Attributes:
        filename (str): Path to JSON file to parse.
        data (dict[str, Any]): Dictionary gotten from the output of loading the
            json file.
    """
    filename: str
    data: list[dict[str, Any]] = Field(default_factory=list)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def model_post_init(self, __context: Any) -> None:
        """Ingests JSON data.

        Gets the data from the JSON file and stores it for later use.
        """
        with open(self.filename) as file:
            self.data = json.load(file)

    @abstractmethod
    def validate_file(self) -> bool:
        """Validates JSON file using a JSON schema."""
        pass

    @abstractmethod
    def get_data(self) -> list[Any]:
        """Transforms the dictionary with the JSON data into the desired data
        types."""
        pass


class InputFileParser(JsonParser):
    """Parser for the input JSON file.

    Validates the file containing the prompts against the prompt JSON schema
    and extracts the prompt strings from it.
    """
    def validate_file(self) -> bool:
        """Validates JSON file using a JSON schema."""
        try:
            with open('src/parser/prompt_schema.json') as schema:
                jsonschema.validate(
                    instance=self.data,
                    schema=json.load(schema)
                )
                return True
        except jsonschema.ValidationError as e:
            raise SchemaError(str(e))

        return False

    def get_data(self) -> list[str]:
        """Transforms the dictionary with the JSON data into the desired data
        types.

        Returns:
            list[str]: List of prompt strings.
        """
        return [value['prompt'] for value in self.data]


class FuncDefParser(JsonParser):
    """Parser for the function definition JSON file.

    Validates the file containing the function definitions against the
    function definition JSON schema and converts each entry into a
    FuncDefData object.
    """
    def validate_file(self) -> bool:
        """Validates JSON file using a JSON schema."""
        try:
            with open('src/parser/function_definition_schema.json') as schema:
                jsonschema.validate(
                    instance=self.data,
                    schema=json.load(schema)
                )
                return True
        except jsonschema.ValidationError as e:
            raise SchemaError(str(e))

        return False

    def get_data(self) -> list[FuncDefData]:
        """Transforms the dictionary with the JSON data into the desired data
        types.

        Returns:
            list[FuncDefData]: list of all functions from JSON file."""
        return [FuncDefData.model_validate(item) for item in self.data]

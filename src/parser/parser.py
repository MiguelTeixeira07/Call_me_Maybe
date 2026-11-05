from .imports import *
from .exceptions import ParsingError
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
    data: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def model_post_init(self, __context) -> None:
        """Ingests JSON data.
        
        Gets the data from the JSON file and stores it for later use.
        """
        with open(self.filename) as file:
            self.data: dict[str, str] = json.load(file)

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
    def validate_file(self) -> bool:
        """Validates JSON file using a JSON schema."""
        ...

    def get_data(self) -> list[str]:
        """Transforms the dictionary with the JSON data into the desired data
        types.
        
        Returns:
            list[str]: List of prompt strings.
        """
        return [value['prompt'] for value in self.data]


class FuncDefParser(JsonParser):
    def validate_file(self) -> bool:
        ...

    def get_data(self) -> list[FuncDefData]:
        """Transforms the dictionary with the JSON data into the desired data
        types.
        
        Returns:
            list[FuncDefData]: list of all functions from JSON file."""
        return [FuncDefData.model_validate(item) for item in self.data]

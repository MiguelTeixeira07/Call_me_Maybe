from typing import Literal
from pydantic import (
    BaseModel,
    model_validator,
    field_validator,
    ConfigDict,
    Field
)
from .exceptions import ArgumentParseError


class Args(BaseModel):
    """Validated command-line arguments.

    Attributes:
        func_def_file (str): Path to the function definition JSON file.
        input_file (str): Path to the input JSON file with the prompts.
        output_file (str): Path to the output JSON file.
    """
    func_def_file: str
    input_file: str
    output_file: str

    @model_validator(mode='after')
    def validator(self) -> 'Args':
        """Validates that all file paths point to JSON files.

        Returns:
            Args: The validated instance.

        Raises:
            ArgumentParseError: If any of the file paths does not end with
                '.json'.
        """
        if any(s for s in [
            self.func_def_file,
            self.output_file,
            self.input_file
        ] if len(s) > 4 and not s.endswith('.json')):
            raise ArgumentParseError('All input files must be json files')

        for file in [self.func_def_file, self.input_file, self.output_file]:
            try:
                if file == self.output_file:
                    fd = open(file, 'w')
                else:
                    fd = open(file)
            except PermissionError:
                raise ArgumentParseError(
                    f'Not enough permissions to "{file}"'
                )
            except FileNotFoundError:
                raise ArgumentParseError(f'Path to file "{file}" is not valid')
            finally:
                fd.close()

        return self


class FuncDefData(BaseModel):
    """Definition of a function that can be called.

    Attributes:
        name (str): Function name. Must start with "fn_".
        description (str): Description of what the function does.
        parameters (dict[str, Types]): Parameter types, keyed by parameter
            name.
        returns (Types): Return type of the function.
        tokens (list[int]): Token ids associated with the function.
    """
    class Types(BaseModel):
        """Type of a parameter or return value.

        Attributes:
            type (Literal['number', 'string']): Name of the type.
        """
        type: Literal['number', 'string']

    name: str
    description: str
    parameters: dict[str, Types]
    returns: Types
    tokens: list[int] = Field(default=[])

    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)

    @field_validator('name', mode='after')
    @classmethod
    def name_validator(cls, value: str) -> str:
        """Validates the function name.

        Args:
            value (str): Function name to validate.

        Returns:
            str: The validated function name.

        Raises:
            ValueError: If the name does not start with "fn_".
        """
        if not value.startswith('fn_'):
            raise ValueError('Function name must start with "fn_"')
        return value

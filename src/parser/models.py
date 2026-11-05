from .imports import model_validator, BaseModel, ConfigDict, Literal
from .exceptions import ArgumentParseError


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
            raise ArgumentParseError('All input files must be json files')

        return self


class FuncDefData(BaseModel):
    class Types(BaseModel):
        type: Literal['number', 'string']

    name: str
    description: str
    parameters: dict[str, Types]
    returns: Types

    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)

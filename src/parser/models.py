from .imports import *
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
    tokens: list[int] = Field(default=[])

    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)

    @field_validator('name', mode='after')
    @classmethod
    def name_validator(cls, value: str) -> str:
        if not value.startswith('fn_'):
            raise ValueError('Function name must start with "fn_"')
        return value

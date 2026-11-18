from pydantic import BaseModel, model_validator


class Func(BaseModel):
    """Result of a function call chosen for a prompt.

    Attributes:
        prompt (str): Prompt the function was chosen for.
        name (str): Name of the chosen function.
        params (dict[str, float | str]): Generated parameter values, keyed by
            parameter name.
    """
    prompt: str
    name: str
    params: dict[str, str]

    @model_validator(mode='after')
    def param_formatter(self) -> 'Func':
        for key, param in self.params.items():
            param = param.replace('\\', '\\\\')
            self.params[key] = param

            if param.isnumeric():
                self.params[key] = str(float(param))
            else:
                self.params[key] = f'"{param}"'

        return self

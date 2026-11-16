from pydantic import BaseModel


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

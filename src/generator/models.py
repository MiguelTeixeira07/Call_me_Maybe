from pydantic import BaseModel, Field


class Func(BaseModel):
    prompt: str
    name: str
    params: dict[str, float | str]

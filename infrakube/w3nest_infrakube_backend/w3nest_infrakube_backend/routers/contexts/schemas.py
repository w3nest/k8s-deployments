from pydantic import BaseModel


class Context(BaseModel):
    cluster: str
    user: str
    name: str


class ContextList(BaseModel):
    items: list[Context]

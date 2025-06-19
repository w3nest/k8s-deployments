from pydantic import BaseModel


class GuestUser(BaseModel):
    id: str
    username: str
    createdTimestamp: int

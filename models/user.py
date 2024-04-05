from . import BaseModel

class User(BaseModel):
    id: int
    name: str 
    password: str
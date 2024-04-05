from . import BaseModel

class User(BaseModel):
    user_id: int
    name: str 
    password: str
    is_admin: bool
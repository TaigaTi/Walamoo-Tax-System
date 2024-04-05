from . import BaseModel

class User(BaseModel):
    user_id: str
    name: str 
    password: str
    is_admin: bool
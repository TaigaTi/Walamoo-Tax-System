from . import BaseModel

class Logs(BaseModel):
    user_id: str
    name: str
    activity: str
    time: str
    admin: bool
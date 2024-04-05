from . import BaseModel

class Alert(BaseModel):
    min_tax: int 
    max_tax: int 
    min_revenue: int
    check_pay: bool 
    check_no_pay: bool
    deadline_month: str
    notify: bool
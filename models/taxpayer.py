from . import BaseModel

class TaxPayer(BaseModel):
    payer_id: str 
    company: str
    street: str
    city: str
    country: str
    tax: int
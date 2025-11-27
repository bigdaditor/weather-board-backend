from datetime import datetime
from pydantic import BaseModel


class SaleCreate(BaseModel):
    input_date: str
    amount: int
    payment_type: str


class SaleRead(BaseModel):
    id: int
    input_date: str
    amount: int
    payment_type: str
    created_at: datetime

    class Config:
        from_attributes = True  # ORM 객체에서 바로 변환
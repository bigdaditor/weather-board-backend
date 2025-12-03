from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class Sale(SQLModel, table=True):
    __tablename__ = "sale"  # 기존 sale 테이블 사용

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    input_date: str
    amount: int
    payment_type: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sync_status: int = 0

class SaleCreate(SQLModel):
    input_date: str
    amount: int
    payment_type: str
    created_at: datetime = datetime.now()
    sync_status: int = 0

class SaleUpdate(SQLModel):
    input_date: str
    amount: int
    payment_type: str
    sync_status: int = 0

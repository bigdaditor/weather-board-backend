from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class SaleBase(SQLModel):
    input_date: str
    amount: int
    payment_type: str

class Sale(SaleBase, table=True):
    __tablename__ = "sale"  # 기존 sale 테이블 사용

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sync_status: int = 0

class SaleCreate(SQLModel):
    pass

class SaleUpdate(SQLModel):
    sync_status: Optional[int] = None

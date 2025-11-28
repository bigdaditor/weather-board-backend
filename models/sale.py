from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class Sale(SQLModel, table=True):
    __tablename__ = "sale"  # 기존 sale 테이블 사용

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    input_date: str  # TEXT NOT NULL
    amount: int      # INTEGER NOT NULL
    payment_type: str  # TEXT NOT NULL
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sync_status: int = 0

class SaleCreate(SQLModel):
    input_date: str
    amount: int
    payment_type: str

class SaleUpdate(SQLModel):
    input_date: Optional[str] = None
    amount: Optional[int] = None
    payment_type: Optional[str] = None
    sync_status: Optional[int] = None

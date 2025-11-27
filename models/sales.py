from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String
from core.db import Base


class Sale(Base):
    __tablename__ = "sale"  # 기존 sales 테이블 사용

    id = Column(Integer, primary_key=True, index=True)
    input_date = Column(String, nullable=False)      # TEXT NOT NULL
    amount = Column(Integer, nullable=False)         # INTEGER NOT NULL
    payment_type = Column(String, nullable=False)    # TEXT NOT NULL
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    sync_status = Column(Integer, nullable=True, default=0)
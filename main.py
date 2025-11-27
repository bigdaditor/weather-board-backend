import os
from datetime import date
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from core.db import Base, engine, get_db
from models.sales import Sale
from schemas.sales import SaleCreate, SaleRead
from utils.weather_sync import request_weather
from dotenv import load_dotenv

load_dotenv()

# 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello WeatherBoard"}


@app.get("/sales/list", response_model=list[SaleRead])
def list_sales(
    date_from: date | None = None,
    date_to: date | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Sale)

    if date_from is not None:
        query = query.filter(Sale.input_date >= date_from.isoformat())
    if date_to is not None:
        query = query.filter(Sale.input_date <= date_to.isoformat())

    sales = query.order_by(Sale.input_date.desc(), Sale.id.desc()).all()
    return sales


@app.post("/sales/add", response_model=SaleRead)
def add_sales(
    sale: SaleCreate,
    db: Session = Depends(get_db),
):
    new_sale = Sale(
        input_date=sale.input_date,
        amount=sale.amount,
        payment_type=sale.payment_type,
    )

    db.add(new_sale)
    db.commit()
    db.refresh(new_sale)

    if not new_sale.id:
        raise HTTPException(status_code=500, detail="매출 저장에 실패했습니다.")

    return new_sale

@app.post("/admin/weather/sync")
def trigger_weather_sync(
    db: Session = Depends(get_db),
):
    """
    sales.weather가 비어있는 레코드들에 대해
    기상청 단기예보를 호출하여 날씨 정보를 동기화한다.
    """

    request_weather(db=db)
    return {"ok": True}
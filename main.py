from fastapi import FastAPI
from sqlmodel import SQLModel
from core.db import engine, SessionDep
from dotenv import load_dotenv
from models.sale import Sale, SaleCreate, SaleUpdate
from service.sale import crate_sale, update_sale
load_dotenv()

# 테이블 생성
SQLModel.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello WeatherBoard"}

@app.post("/sale", response_model=Sale)
def create_sale_point(
    session: SessionDep,
    sale: SaleCreate,
) -> Sale:
    return crate_sale(session, sale)

@app.patch("/sale/{sale_id}", response_model=Sale)
def update_sale_point(
    session: SessionDep,
    sale_id: int,
    sale: SaleUpdate,
) -> Sale:
    return update_sale(session, sale_id, sale)
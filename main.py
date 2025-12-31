from fastapi import FastAPI, Query
from sqlmodel import SQLModel, Session
from starlette.middleware.cors import CORSMiddleware

from core.db import engine, SessionDep
from dotenv import load_dotenv
from models.sale import Sale, SaleCreate, SaleUpdate, SaleListResponse
from models.weather import Weather
from service.sale import crate_sale, update_sale, get_sales, get_sale
from service.weather import create_weather, read_weathers_by_input_date
from typing import List, Any

load_dotenv()

# 테이블 생성
SQLModel.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],      # OPTIONS, POST, GET 전부 허용
    allow_headers=["*"],      # Content-Type, Authorization 등
)
@app.get("/")
async def root():
    return {"message": "Hello WeatherBoard"}

@app.post("/sale", response_model=Sale)
def create_sale_point(
    session: SessionDep,
    sale: SaleCreate,
) -> Sale:
    return crate_sale(session, sale)

@app.get("/sale", response_model=SaleListResponse)
def get_sales_point(
    session: SessionDep,
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(10, ge=1, le=100, description="페이지당 항목 수")
) -> SaleListResponse:
    return get_sales(session, page, page_size)

@app.get("/sale/{sale_id}", response_model=Sale)
def get_sale_point(
    session: SessionDep,
    sale_id: int,
) -> Sale:
    return get_sale(session, sale_id)

@app.patch("/sale/{sale_id}", response_model=Sale)
def update_sale_point(
    session: SessionDep,
    sale_id: int,
    sale: SaleUpdate,
) -> Sale:
    return update_sale(session, sale_id, sale)

@app.post("/weather", response_model=List[Weather])
def create_weather_point(
    session: SessionDep,
) -> List[Weather]:
    return create_weather(session)


@app.get("/weather", response_model=List[Weather])
def get_weathers_point(
    session: SessionDep,
) -> List[Weather]:
    return read_weathers_by_input_date(session)

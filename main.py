from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlmodel import SQLModel
from starlette.middleware.cors import CORSMiddleware

from core.db import engine, SessionDep
from dotenv import load_dotenv
from models.sale import Sale, SaleCreate, SaleUpdate, SaleDelete, SaleListResponse, MonthlySaleResponse
from models.weather import Weather
from models.sale_statistics import SaleStatisticsResponse
from service.sale import crate_sale, update_sale, get_sales, get_sale, delete_sale, get_sale_by_month
from service.weather import create_weather, read_weathers_by_input_date
from service.sale_statistics import get_statistics, get_statistics_summary
from typing import List, Any, Optional
from pathlib import Path

load_dotenv()

# 테이블 생성
SQLModel.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],      # OPTIONS, POST, GET 전부 허용
    allow_headers=["*"],      # Content-Type, Authorization 등
)

# 프론트엔드 빌드 파일 경로
FRONTEND_DIST = Path(__file__).parent.parent / "weather-board-frontend" / "dist"

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

@app.get("/sale/month/", response_model=MonthlySaleResponse)
def get_sale_by_month_point(
    session: SessionDep,
    key: str,
) -> MonthlySaleResponse:
    return get_sale_by_month(session, key)

@app.get("/sale/{sale_id}", response_model=Sale)
def get_sale_point(
    session: SessionDep,
    sale_id: int,
) -> Sale:
    return get_sale(session, sale_id)

@app.patch("/sale", response_model=Sale)
def update_sale_point(
    session: SessionDep,
    sale: SaleUpdate,
) -> Sale:
    return update_sale(session, sale)

@app.delete("/sale", response_model=Sale)
def delete_sale_point(
        session: SessionDep,
        sale: SaleDelete,
) -> Sale:
    return delete_sale(session, sale)

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


# 통계 API
@app.get("/statistics", response_model=List[SaleStatisticsResponse])
def get_statistics_point(
    session: SessionDep,
    period_type: Optional[str] = Query(None, description="기간 타입 (week/month)"),
    payment_type: Optional[str] = Query(None, description="결제 타입 (all/etc/...)"),
    start_date: Optional[str] = Query(None, description="조회 시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="조회 종료 날짜 (YYYY-MM-DD)"),
) -> List[SaleStatisticsResponse]:
    """
    판매 통계 조회

    - period_type: 'week' (주별) 또는 'month' (월별)
    - payment_type: 'all' (전체) 또는 특정 결제 타입
    - start_date, end_date: 날짜 범위 필터

    여러 조건을 조합하여 조회 가능
    """
    return get_statistics(
        session=session,
        period_type=period_type,
        payment_type=payment_type,
        start_date=start_date,
        end_date=end_date
    )


@app.get("/statistics/summary/{period_type}", response_model=List[SaleStatisticsResponse])
def get_statistics_summary_point(
    session: SessionDep,
    period_type: str,
    payment_type: str = Query("all", description="결제 타입"),
) -> List[SaleStatisticsResponse]:
    """
    통계 요약 조회

    - period_type: 'week' (주별) 또는 'month' (월별)
    - payment_type: 기본값 'all' (전체)
    """
    return get_statistics_summary(
        session=session,
        period_type=period_type,
        payment_type=payment_type
    )


# 프론트엔드 정적 파일 서빙 (운영 환경)
if FRONTEND_DIST.exists():
    # React 빌드 파일의 assets 폴더 서빙
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    # SPA를 위한 catch-all 라우트 (모든 경로를 index.html로)
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # API 경로가 아닌 경우에만 index.html 반환
        if not full_path.startswith("sale") and not full_path.startswith("weather") and not full_path.startswith("statistics"):
            index_path = FRONTEND_DIST / "index.html"
            if index_path.exists():
                return FileResponse(index_path)
        return {"message": "Not Found"}
else:
    # 개발 환경: 프론트엔드가 빌드되지 않은 경우 안내 메시지
    @app.get("/")
    async def root():
        return {
            "message": "Weather Board API",
            "note": "프론트엔드를 사용하려면 먼저 빌드하세요: npm run build",
            "dev_mode": "개발 모드에서는 프론트엔드를 별도로 실행하세요: npm run dev"
        }

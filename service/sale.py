from fastapi import HTTPException
from collections import defaultdict
from math import ceil

from models.sale import Sale, SaleCreate, SaleUpdate, SaleListResponse, DailySaleByPaymentType
from core.db import SessionDep
from sqlmodel import select
from typing import List

def crate_sale(
    session: SessionDep,
    data: SaleCreate,
) -> Sale:
    sale = Sale(**data.model_dump())
    session.add(sale)
    session.commit()
    session.refresh(sale)
    return sale

def get_sales(
    session: SessionDep,
    page: int = 1,
    page_size: int = 10,
) -> SaleListResponse:
    # 모든 판매 데이터 조회
    sales = session.exec(
        select(Sale)
        .order_by(Sale.input_date)
    ).all()

    if not sales:
        raise HTTPException(status_code=404, detail="Sales not found")

    # 날짜별로 그룹화하여 결제 타입별 금액 집계
    daily_sales_dict = defaultdict(lambda: defaultdict(int))

    for sale in sales:
        daily_sales_dict[sale.input_date][sale.payment_type] += sale.amount

    # DailySaleByPaymentType 리스트 생성
    daily_sales_list = []
    for date, payment_types in sorted(daily_sales_dict.items()):
        total_amount = sum(payment_types.values())
        daily_sales_list.append(
            DailySaleByPaymentType(
                date=date,
                payment_types=dict(payment_types),
                total_amount=total_amount
            )
        )

    # 페이지네이션 계산
    total = len(daily_sales_list)
    total_pages = ceil(total / page_size)

    # 페이지 범위 검증
    if page < 1:
        page = 1
    if page > total_pages and total_pages > 0:
        page = total_pages

    # 페이지네이션 적용
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_data = daily_sales_list[start_idx:end_idx]

    return SaleListResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        data=paginated_data
    )

def get_sale(
    session: SessionDep,
    sale_id: int,
) -> Sale:
    sale = session.get(Sale, sale_id)

    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale

def update_sale(
    session: SessionDep,
    sale_id: int,
    data: SaleUpdate,
) -> Sale:
    sale = session.get(Sale, sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(sale, key, value)

    session.add(sale)
    session.commit()
    session.refresh(sale)
    return sale
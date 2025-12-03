from fastapi import HTTPException

from models.sale import Sale, SaleCreate, SaleUpdate
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
) -> List[Sale]:
    sales = session.exec(
        select(Sale)
    ).all()

    if not sales:
        raise HTTPException(status_code=404, detail="Sales not found")
    return sales

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
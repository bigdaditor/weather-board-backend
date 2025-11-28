from fastapi import HTTPException

from models.sale import Sale, SaleCreate, SaleUpdate
from core.db import SessionDep

def crate_sale(
    session: SessionDep,
    data: SaleCreate,
) -> Sale:
    sale = Sale(**data.dict())
    session.add(sale)
    session.commit()
    session.refresh(sale)
    return sale

def update_sale(
    session: SessionDep,
    sale_id: int,
    data: SaleUpdate,
) -> Sale:
    sale = session.get(Sale, sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(sale, key, value)

    session.add(sale)
    session.commit()
    session.refresh(sale)
    return sale
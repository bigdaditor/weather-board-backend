from typing import Annotated

from fastapi import Depends
from sqlmodel import create_engine, Session

DATABASE_URL = "sqlite:///./sales.db"

engine = create_engine(DATABASE_URL, echo=True)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

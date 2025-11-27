from sqlalchemy import Column, Integer, String, ForeignKey, Float
from core.db import Base


class Weather(Base):
    __tablename__ = "weather"

    date = Column(String, nullable=False, primary_key=True)
    avg_temp = Column(Float, nullable=False)
    min_temp = Column(Float, nullable=False)
    max_temp = Column(Float, nullable=False)
    sum_rain = Column(Float, nullable=False)
    avg_humidity = Column(Float, nullable=False)
    summary = Column(String, nullable=True)
    one_hour_rain = Column(Float, nullable=False)



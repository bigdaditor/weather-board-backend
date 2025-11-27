from datetime import date, datetime
import os
from dotenv import load_dotenv
import httpx
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional

from sqlalchemy import update

from models.weather import Weather
from utils.convert import date_format_change
from utils.weather_classifier import classify_sky, classify_rain

URL = "http://apis.data.go.kr/1360000/AsosDalyInfoService/getWthrDataList"
load_dotenv()

def request_weather(
    db: Session,
):
    from models.sales import Sale
    sales = (
        db.query(Sale)
        .filter(Sale.sync_status == 0)
        .order_by("input_date")
        .limit(6)
    )

    if not sales:
        print("No sales found")
        return

    start_dt = date_format_change(
        date=sales[0].input_date,
        current_form="%Y-%m-%d",
        new_form="%Y%m%d"
    )
    end_dt = date_format_change(
        date=sales[5].input_date,
        current_form="%Y-%m-%d",
        new_form="%Y%m%d")
    response = fetch_weather_data(start_dt, end_dt)

    for item in response["items"]["item"]:
        one_hour_rain = float(item["hr1MaxRn"] if item["hr1MaxRn"] !="" else 0)
        avg_total_cloud = float(item["avgTca"] if item["avgTca"] != "" else 0)

        summary = classify_sky(avg_total_cloud) + " / " + classify_rain(one_hour_rain)

        new_weather = Weather(
            date = item["tm"],
            avg_temp= float(item["avgTa"]),
            min_temp= float(item["minTa"]),
            max_temp= float(item["maxTa"]),
            one_hour_rain=one_hour_rain,
            sum_rain= float(item["sumRn"] if item["sumRn"] !="" else 0),
            avg_humidity= float(item["avgRhm"]),
            summary= summary
        )
        db.add(new_weather)

        db.execute(
            update(Sale).
            where(Sale.input_date == item["tm"]).
            values(sync_status=1)
        )

        db.commit()
        db.refresh(new_weather)
    return response


def fetch_weather_data(
    start_date: str,
    end_date: str,
):
    http = httpx.Client()
    service_key = os.getenv("KMA_SERVICE_KEY")
    params = {
        "serviceKey": service_key,
        "numOfRows": 10,
        "pageNo": 1,
        "dataType": "JSON",
        "dataCd": "ASOS",
        "dateCd": "DAY",
        "startDt": start_date,
        "endDt": end_date,
        "stnIds": 108
    }

    response = http.get(URL, params=params)
    data = response.json().get("response")
    header = data.get("header", {})
    if header.get("resultCode") != "00":
        raise Exception("No weather data found")

    body = data.get("body", {})
    return body


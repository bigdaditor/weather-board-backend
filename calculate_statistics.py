#!/usr/bin/env python3
"""
판매 통계 계산 및 저장 스크립트
주별(월~토), 월별, 결제 타입별로 통계를 계산하여 sale_statistics 테이블에 저장
"""

import sqlite3
from datetime import datetime, timedelta, timezone
from collections import defaultdict


def get_monday_of_week(date_str):
    """주어진 날짜가 속한 주의 월요일을 반환 (월~토 기준)"""
    date = datetime.strptime(date_str, "%Y-%m-%d")
    # weekday(): 월요일=0, 토요일=5, 일요일=6
    weekday = date.weekday()

    # 일요일(6)은 다음 주 월요일로 계산
    if weekday == 6:  # 일요일
        monday = date + timedelta(days=1)
    else:
        monday = date - timedelta(days=weekday)

    return monday.strftime("%Y-%m-%d")


def get_saturday_of_week(monday_str):
    """월요일 날짜로부터 토요일 날짜를 반환"""
    monday = datetime.strptime(monday_str, "%Y-%m-%d")
    saturday = monday + timedelta(days=5)
    return saturday.strftime("%Y-%m-%d")


def get_month_range(date_str):
    """주어진 날짜가 속한 월의 시작일과 종료일 반환"""
    date = datetime.strptime(date_str, "%Y-%m-%d")
    year = date.year
    month = date.month

    # 월의 첫날
    first_day = datetime(year, month, 1).strftime("%Y-%m-%d")

    # 월의 마지막 날
    if month == 12:
        last_day = datetime(year, 12, 31).strftime("%Y-%m-%d")
    else:
        next_month = datetime(year, month + 1, 1)
        last_day = (next_month - timedelta(days=1)).strftime("%Y-%m-%d")

    return first_day, last_day


def calculate_statistics():
    """판매 데이터로부터 통계 계산"""
    conn = sqlite3.connect('sales.db')
    cursor = conn.cursor()

    # 기존 통계 데이터 삭제 (재계산)
    cursor.execute("DELETE FROM sale_statistics")

    # 모든 판매 데이터 조회
    cursor.execute("""
        SELECT input_date, amount, payment_type
        FROM sale
        ORDER BY input_date
    """)

    sales = cursor.fetchall()

    if not sales:
        print("판매 데이터가 없습니다.")
        conn.close()
        return

    # 주별 집계 (전체)
    weekly_all = defaultdict(lambda: {'total': 0, 'count': 0})
    # 주별 집계 (결제 타입별)
    weekly_by_type = defaultdict(lambda: defaultdict(lambda: {'total': 0, 'count': 0}))

    # 월별 집계 (전체)
    monthly_all = defaultdict(lambda: {'total': 0, 'count': 0})
    # 월별 집계 (결제 타입별)
    monthly_by_type = defaultdict(lambda: defaultdict(lambda: {'total': 0, 'count': 0}))

    for date, amount, payment_type in sales:
        # 주별 집계
        monday = get_monday_of_week(date)
        saturday = get_saturday_of_week(monday)
        week_key = (monday, saturday)

        weekly_all[week_key]['total'] += amount
        weekly_all[week_key]['count'] += 1

        weekly_by_type[week_key][payment_type]['total'] += amount
        weekly_by_type[week_key][payment_type]['count'] += 1

        # 월별 집계
        month_start, month_end = get_month_range(date)
        month_key = (month_start, month_end)

        monthly_all[month_key]['total'] += amount
        monthly_all[month_key]['count'] += 1

        monthly_by_type[month_key][payment_type]['total'] += amount
        monthly_by_type[month_key][payment_type]['count'] += 1

    # 통계 데이터 삽입
    now = datetime.now(timezone.utc).isoformat()

    # 주별 통계 (전체)
    for (start, end), data in weekly_all.items():
        avg = data['total'] / data['count'] if data['count'] > 0 else 0
        cursor.execute("""
            INSERT INTO sale_statistics
            (period_type, period_start, period_end, payment_type, total_amount, transaction_count, avg_amount, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ('week', start, end, 'all', data['total'], data['count'], avg, now, now))

    # 주별 통계 (결제 타입별)
    for (start, end), types in weekly_by_type.items():
        for payment_type, data in types.items():
            avg = data['total'] / data['count'] if data['count'] > 0 else 0
            cursor.execute("""
                INSERT INTO sale_statistics
                (period_type, period_start, period_end, payment_type, total_amount, transaction_count, avg_amount, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, ('week', start, end, payment_type, data['total'], data['count'], avg, now, now))

    # 월별 통계 (전체)
    for (start, end), data in monthly_all.items():
        avg = data['total'] / data['count'] if data['count'] > 0 else 0
        cursor.execute("""
            INSERT INTO sale_statistics
            (period_type, period_start, period_end, payment_type, total_amount, transaction_count, avg_amount, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ('month', start, end, 'all', data['total'], data['count'], avg, now, now))

    # 월별 통계 (결제 타입별)
    for (start, end), types in monthly_by_type.items():
        for payment_type, data in types.items():
            avg = data['total'] / data['count'] if data['count'] > 0 else 0
            cursor.execute("""
                INSERT INTO sale_statistics
                (period_type, period_start, period_end, payment_type, total_amount, transaction_count, avg_amount, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, ('month', start, end, payment_type, data['total'], data['count'], avg, now, now))

    conn.commit()

    # 결과 요약
    cursor.execute("SELECT COUNT(*) FROM sale_statistics WHERE period_type = 'week'")
    week_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM sale_statistics WHERE period_type = 'month'")
    month_count = cursor.fetchone()[0]

    print(f"통계 계산 완료!")
    print(f"- 주별 통계: {week_count}건")
    print(f"- 월별 통계: {month_count}건")
    print(f"- 총 통계: {week_count + month_count}건")

    conn.close()


def create_table_if_not_exists():
    """통계 테이블이 없으면 생성"""
    conn = sqlite3.connect('sales.db')
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sale_statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            period_type TEXT NOT NULL,
            period_start TEXT NOT NULL,
            period_end TEXT NOT NULL,
            payment_type TEXT NOT NULL,
            total_amount INTEGER NOT NULL,
            transaction_count INTEGER NOT NULL,
            avg_amount REAL NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    # 인덱스 생성 (조회 성능 향상)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_statistics_period
        ON sale_statistics(period_type, period_start, period_end)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_statistics_payment_type
        ON sale_statistics(payment_type)
    """)

    conn.commit()
    conn.close()
    print("통계 테이블 준비 완료")


if __name__ == "__main__":
    print("=" * 50)
    print("판매 통계 계산 스크립트")
    print("=" * 50)

    create_table_if_not_exists()
    calculate_statistics()

    print("\n통계 데이터가 sale_statistics 테이블에 저장되었습니다.")
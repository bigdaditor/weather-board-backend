from typing import List, Optional
from sqlmodel import Session, select
from models.sale_statistics import SaleStatistics, SaleStatisticsResponse


def get_statistics(
    session: Session,
    period_type: Optional[str] = None,
    payment_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[SaleStatisticsResponse]:
    """
    통계 데이터 조회

    Args:
        session: DB 세션
        period_type: 기간 타입 ('week' 또는 'month')
        payment_type: 결제 타입 ('all', 'etc', 등)
        start_date: 조회 시작 날짜 (YYYY-MM-DD)
        end_date: 조회 종료 날짜 (YYYY-MM-DD)

    Returns:
        통계 데이터 리스트
    """
    query = select(SaleStatistics)

    # 기간 타입 필터
    if period_type:
        query = query.where(SaleStatistics.period_type == period_type)

    # 결제 타입 필터
    if payment_type:
        query = query.where(SaleStatistics.payment_type == payment_type)

    # 날짜 범위 필터
    if start_date:
        query = query.where(SaleStatistics.period_start >= start_date)

    if end_date:
        query = query.where(SaleStatistics.period_end <= end_date)

    # 정렬: 기간 시작일 기준 오름차순
    query = query.order_by(SaleStatistics.period_start)

    results = session.exec(query).all()

    return [
        SaleStatisticsResponse(
            period_type=stat.period_type,
            period_start=stat.period_start,
            period_end=stat.period_end,
            payment_type=stat.payment_type,
            total_amount=stat.total_amount,
            transaction_count=stat.transaction_count,
            avg_amount=stat.avg_amount,
            created_at=stat.created_at,
            updated_at=stat.updated_at,
        )
        for stat in results
    ]


def get_statistics_summary(
    session: Session,
    period_type: str,
    payment_type: str = "all"
) -> List[SaleStatisticsResponse]:
    """
    특정 기간 타입과 결제 타입의 전체 통계 조회

    Args:
        session: DB 세션
        period_type: 기간 타입 ('week' 또는 'month')
        payment_type: 결제 타입 (기본값: 'all')

    Returns:
        통계 데이터 리스트
    """
    return get_statistics(
        session=session,
        period_type=period_type,
        payment_type=payment_type
    )
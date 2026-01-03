# Weather Board Backend API 명세서

## Base URL
```
http://localhost:8000
```

## 목차
- [Sale API](#sale-api)
- [Statistics API](#statistics-api)
- [Weather API](#weather-api)

---

## Sale API

### 1. 판매 데이터 생성
새로운 판매 레코드를 생성합니다.

**Endpoint**
```
POST /sale
```

**Request Body**
```json
{
  "input_date": "2024-01-15",
  "amount": 50000,
  "payment_type": "card",
  "created_at": "2024-01-15T10:30:00",
  "sync_status": 0
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| input_date | string | O | 판매 날짜 (YYYY-MM-DD) |
| amount | integer | O | 판매 금액 |
| payment_type | string | O | 결제 방법 (예: card, cash) |
| created_at | datetime | O | 생성 시각 |
| sync_status | integer | O | 동기화 상태 (기본값: 0) |

**Response**
```json
{
  "id": 1,
  "input_date": "2024-01-15",
  "amount": 50000,
  "payment_type": "card",
  "created_at": "2024-01-15T10:30:00",
  "sync_status": 0
}
```

**Status Codes**
- `200 OK`: 성공

---

### 2. 판매 데이터 목록 조회 (페이지네이션)
날짜별로 그룹화된 판매 데이터를 페이지네이션과 함께 조회합니다.

**Endpoint**
```
GET /sale?page=1&page_size=10
```

**Query Parameters**
| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| page | integer | X | 1 | 페이지 번호 (최소: 1) |
| page_size | integer | X | 10 | 페이지당 항목 수 (범위: 1-100) |

**Response**
```json
{
  "total": 50,
  "page": 1,
  "page_size": 10,
  "total_pages": 5,
  "data": [
    {
      "date": "2024-01-15",
      "payment_types": {
        "card": 150000,
        "cash": 80000
      },
      "total_amount": 230000
    },
    {
      "date": "2024-01-16",
      "payment_types": {
        "card": 120000,
        "cash": 60000,
        "transfer": 40000
      },
      "total_amount": 220000
    }
  ]
}
```

**Response Fields**
| 필드 | 타입 | 설명 |
|------|------|------|
| total | integer | 전체 날짜 수 |
| page | integer | 현재 페이지 번호 |
| page_size | integer | 페이지당 항목 수 |
| total_pages | integer | 전체 페이지 수 |
| data | array | 날짜별 판매 데이터 목록 |
| data[].date | string | 날짜 |
| data[].payment_types | object | 결제 타입별 금액 (key: 결제방법, value: 금액) |
| data[].total_amount | integer | 해당 날짜의 총 판매 금액 |

**Status Codes**
- `200 OK`: 성공
- `404 Not Found`: 판매 데이터가 없음

---

### 3. 특정 판매 데이터 조회
ID로 특정 판매 레코드를 조회합니다.

**Endpoint**
```
GET /sale/{sale_id}
```

**Path Parameters**
| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| sale_id | integer | O | 판매 레코드 ID |

**Response**
```json
{
  "id": 1,
  "input_date": "2024-01-15",
  "amount": 50000,
  "payment_type": "card",
  "created_at": "2024-01-15T10:30:00",
  "sync_status": 0
}
```

**Status Codes**
- `200 OK`: 성공
- `404 Not Found`: 해당 ID의 판매 데이터가 없음

---

### 4. 판매 데이터 수정
특정 판매 레코드를 수정합니다.

**Endpoint**
```
PATCH /sale/{sale_id}
```

**Path Parameters**
| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| sale_id | integer | O | 판매 레코드 ID |

**Request Body**
```json
{
  "input_date": "2024-01-15",
  "amount": 60000,
  "payment_type": "cash",
  "sync_status": 1
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| input_date | string | O | 판매 날짜 |
| amount | integer | O | 판매 금액 |
| payment_type | string | O | 결제 방법 |
| sync_status | integer | O | 동기화 상태 |

**Response**
```json
{
  "id": 1,
  "input_date": "2024-01-15",
  "amount": 60000,
  "payment_type": "cash",
  "created_at": "2024-01-15T10:30:00",
  "sync_status": 1
}
```

**Status Codes**
- `200 OK`: 성공
- `404 Not Found`: 해당 ID의 판매 데이터가 없음

---

## Statistics API

판매 데이터를 주별(월~토), 월별, 결제 타입별로 집계한 통계를 제공하는 API입니다.

### 통계 데이터 생성

통계 데이터는 `calculate_statistics.py` 스크립트를 실행하여 생성합니다.

```bash
python calculate_statistics.py
```

이 스크립트는:
1. `sale_statistics` 테이블을 생성 (없는 경우)
2. 기존 통계 데이터 삭제 후 재계산
3. `sale` 테이블의 모든 데이터를 읽어서 통계 계산
4. 주별/월별, 전체/결제타입별 통계를 모두 생성

**주의사항:**
- 주 단위는 **월요일부터 토요일**까지입니다
- 일요일은 다음 주의 월요일로 분류됩니다
- 새로운 판매 데이터 추가 시 스크립트를 다시 실행하세요

---

### 1. 통계 조회 (필터링)

여러 조건을 조합하여 통계를 조회합니다.

**Endpoint**
```
GET /statistics
```

**Query Parameters**
| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| period_type | string | X | - | 기간 타입: `week` (주별) 또는 `month` (월별) |
| payment_type | string | X | - | 결제 타입: `all` (전체), `etc` (기타) 등 |
| start_date | string | X | - | 조회 시작 날짜 (YYYY-MM-DD) |
| end_date | string | X | - | 조회 종료 날짜 (YYYY-MM-DD) |

**Response**
```json
[
  {
    "period_type": "week",
    "period_start": "2025-01-06",
    "period_end": "2025-01-11",
    "payment_type": "all",
    "total_amount": 150000,
    "transaction_count": 5,
    "avg_amount": 30000.0,
    "created_at": "2025-01-01T10:00:00",
    "updated_at": "2025-01-01T10:00:00"
  }
]
```

**Response Fields**
| 필드 | 타입 | 설명 |
|-----|------|------|
| period_type | string | 기간 타입 (`week` 또는 `month`) |
| period_start | string | 기간 시작일 (YYYY-MM-DD) |
| period_end | string | 기간 종료일 (YYYY-MM-DD) |
| payment_type | string | 결제 타입 (`all`, `etc` 등) |
| total_amount | integer | 총 판매액 |
| transaction_count | integer | 거래 건수 |
| avg_amount | float | 평균 판매액 |
| created_at | datetime | 통계 생성 시간 |
| updated_at | datetime | 통계 수정 시간 |

**사용 예시**

주별 전체 통계:
```
GET /statistics?period_type=week&payment_type=all
```

월별 특정 결제 타입:
```
GET /statistics?period_type=month&payment_type=etc
```

특정 기간의 통계:
```
GET /statistics?start_date=2025-01-01&end_date=2025-01-31
```

여러 조건 조합:
```
GET /statistics?period_type=week&payment_type=etc&start_date=2025-01-01&end_date=2025-01-31
```

**Status Codes**
- `200 OK`: 성공

---

### 2. 통계 요약 조회

특정 기간 타입의 전체 통계를 간편하게 조회합니다.

**Endpoint**
```
GET /statistics/summary/{period_type}
```

**Path Parameters**
| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| period_type | string | O | `week` (주별) 또는 `month` (월별) |

**Query Parameters**
| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| payment_type | string | X | all | 결제 타입 |

**Response**

위의 통계 조회 API와 동일한 형식

**사용 예시**

주별 전체 통계:
```
GET /statistics/summary/week
```

월별 전체 통계:
```
GET /statistics/summary/month
```

주별 특정 결제 타입:
```
GET /statistics/summary/week?payment_type=etc
```

**Status Codes**
- `200 OK`: 성공

---

### 사용 시나리오

#### 1. 주별 매출 추이 확인
```
GET /statistics?period_type=week&payment_type=all
```
월요일부터 토요일까지의 주별 전체 매출을 확인합니다.

#### 2. 특정 월의 결제 타입별 비교
```
GET /statistics?period_type=month&start_date=2025-01-01&end_date=2025-01-31
```
2025년 1월의 모든 결제 타입별 통계를 조회합니다.

#### 3. 월별 평균 거래액 분석
```
GET /statistics/summary/month
```
모든 월의 평균 거래액(`avg_amount`)을 확인할 수 있습니다.

---

### 통계 자동 업데이트

새로운 판매 데이터가 추가되면 통계를 재계산해야 합니다:

```bash
python calculate_statistics.py
```

자동화 예시 (crontab):
```bash
# 매일 자정에 통계 재계산
0 0 * * * cd /path/to/weather-board-backend && python calculate_statistics.py
```

---

## Weather API

### 1. 날씨 데이터 생성
새로운 날씨 레코드를 생성합니다.

**Endpoint**
```
POST /weather
```

**Request Body**
```json
{
  "date": "2024-01-15",
  "avg_temp": 5.5,
  "min_temp": -2.0,
  "max_temp": 12.0,
  "sum_rain": 3.5,
  "avg_humidity": 65.0,
  "one_hour_rain": 2.0
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| date | string | O | 날짜 (YYYY-MM-DD) |
| avg_temp | float | O | 평균 기온 (°C) |
| min_temp | float | O | 최저 기온 (°C) |
| max_temp | float | O | 최고 기온 (°C) |
| sum_rain | float | O | 총 강수량 (mm) |
| avg_humidity | float | O | 평균 습도 (%) |
| one_hour_rain | float | O | 최대 시간당 강수량 (mm) |

**Response**
```json
[
  {
    "date": "2024-01-15",
    "avg_temp": 5.5,
    "min_temp": -2.0,
    "max_temp": 12.0,
    "sum_rain": 3.5,
    "avg_humidity": 65.0,
    "one_hour_rain": 2.0,
    "summary": "흐림, 비"
  }
]
```

**Status Codes**
- `200 OK`: 성공

---

### 2. 날씨 데이터 조회
입력 날짜로 날씨 데이터를 조회합니다.

**Endpoint**
```
GET /weather
```

**Response**
```json
[
  {
    "date": "2024-01-15",
    "avg_temp": 5.5,
    "min_temp": -2.0,
    "max_temp": 12.0,
    "sum_rain": 3.5,
    "avg_humidity": 65.0,
    "one_hour_rain": 2.0,
    "summary": "흐림, 비"
  },
  {
    "date": "2024-01-16",
    "avg_temp": 8.0,
    "min_temp": 3.0,
    "max_temp": 15.0,
    "sum_rain": 0.0,
    "avg_humidity": 55.0,
    "one_hour_rain": 0.0,
    "summary": "맑음"
  }
]
```

**Response Fields**
| 필드 | 타입 | 설명 |
|------|------|------|
| date | string | 날짜 |
| avg_temp | float | 평균 기온 (°C) |
| min_temp | float | 최저 기온 (°C) |
| max_temp | float | 최고 기온 (°C) |
| sum_rain | float | 총 강수량 (mm) |
| avg_humidity | float | 평균 습도 (%) |
| one_hour_rain | float | 최대 시간당 강수량 (mm) |
| summary | string | 날씨 요약 |

**Status Codes**
- `200 OK`: 성공

---

## 공통 사항

### CORS
다음 origin에서의 요청을 허용합니다:
- `http://localhost:5173`
- `http://127.0.0.1:5173`

### 에러 응답
모든 API는 에러 발생 시 다음 형식으로 응답합니다:

```json
{
  "detail": "에러 메시지"
}
```

### 결제 타입 (Payment Types)
일반적으로 사용되는 결제 타입:
- `card`: 카드
- `cash`: 현금
- `transfer`: 이체
- 기타 사용자 정의 타입 가능

### 날짜 형식
모든 날짜는 `YYYY-MM-DD` 형식을 사용합니다.

### 날짜/시간 형식
모든 날짜/시간은 ISO 8601 형식을 사용합니다 (예: `2024-01-15T10:30:00`).

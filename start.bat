@echo off
chcp 65001 >nul
echo ========================================
echo Weather Board 시작 (운영 모드)
echo ========================================
echo.

cd /d %~dp0

REM 가상환경 활성화
if exist .venv\Scripts\activate.bat (
    echo [1/3] Python 가상환경 활성화 중...
    call .venv\Scripts\activate.bat
) else (
    echo 경고: 가상환경을 찾을 수 없습니다. 전역 Python을 사용합니다.
)

REM 프론트엔드 빌드 확인
cd ..\weather-board-frontend
if not exist dist\index.html (
    echo.
    echo [2/3] 프론트엔드 빌드 중...
    echo 잠시만 기다려 주세요...
    call npm run build
    if errorlevel 1 (
        echo.
        echo 오류: 프론트엔드 빌드에 실패했습니다.
        pause
        exit /b 1
    )
) else (
    echo [2/3] 프론트엔드 빌드 확인됨
)

REM 백엔드 서버 실행
cd ..\weather-board-backend
echo.
echo [3/3] 서버 시작 중...
echo.
echo ========================================
echo 서버가 실행되었습니다!
echo 브라우저에서 http://localhost:8000 접속
echo 종료하려면 Ctrl+C를 누르세요
echo ========================================
echo.

python -m uvicorn main:app --host 0.0.0.0 --port 8000

pause

@echo off
chcp 65001 >nul
echo ========================================
echo Weather Board 재빌드 후 시작
echo ========================================
echo.

cd /d %~dp0

REM 가상환경 활성화
if exist .venv\Scripts\activate.bat (
    echo [1/4] Python 가상환경 활성화 중...
    call .venv\Scripts\activate.bat
) else (
    echo 경고: 가상환경을 찾을 수 없습니다.
)

REM 기존 빌드 파일 삭제
cd ..\weather-board-frontend
if exist dist (
    echo [2/4] 기존 빌드 파일 삭제 중...
    rmdir /s /q dist
)

REM 프론트엔드 빌드
echo.
echo [3/4] 프론트엔드 빌드 중...
echo 잠시만 기다려 주세요...
call npm run build
if errorlevel 1 (
    echo.
    echo 오류: 프론트엔드 빌드에 실패했습니다.
    pause
    exit /b 1
)

REM 백엔드 서버 실행
cd ..\weather-board-backend
echo.
echo [4/4] 서버 시작 중...
echo.
echo ========================================
echo 서버가 실행되었습니다!
echo 브라우저에서 http://localhost:8000 접속
echo 종료하려면 Ctrl+C를 누르세요
echo ========================================
echo.

python -m uvicorn main:app --host 0.0.0.0 --port 8000

pause

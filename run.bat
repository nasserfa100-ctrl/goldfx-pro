@echo off
title GoldFX Pro v4.0 - Launcher
color 0A
echo.
echo  =============================================
echo   GoldFX Pro v4.0 - AI Trading System
echo  =============================================
echo.
echo  اختر رقم البورت:
echo.
echo  [1]  Port 8501
echo  [2]  Port 8502
echo  [3]  Port 8503
echo  [4]  Port 8504
echo  [5]  Port 8505
echo  [6]  Port 8506
echo  [7]  Port 8507
echo  [8]  Port 8508
echo  [9]  Port 8509
echo  [10] Port 8510
echo.
set /p choice="اختار رقم (1-10): "

if "%choice%"=="1" set PORT=8501
if "%choice%"=="2" set PORT=8502
if "%choice%"=="3" set PORT=8503
if "%choice%"=="4" set PORT=8504
if "%choice%"=="5" set PORT=8505
if "%choice%"=="6" set PORT=8506
if "%choice%"=="7" set PORT=8507
if "%choice%"=="8" set PORT=8508
if "%choice%"=="9" set PORT=8509
if "%choice%"=="10" set PORT=8510

if "%PORT%"=="" (
    echo رقم غير صحيح!
    pause
    exit /b
)

echo.
echo  جاري التشغيل على http://localhost:%PORT% ...
echo.
streamlit run app.py --server.port %PORT%
pause

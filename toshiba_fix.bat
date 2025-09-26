@echo off
REM Synology Drive Unlocker - Специальный фикс для Toshiba HDWT860
REM Целевое решение для конкретной модели диска

REM ---------- Fix console encoding ----------
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

title Synology Drive Unlocker - Toshiba HDWT860 Fix

echo.
echo ========================================
echo   TOSHIBA HDWT860 SPECIAL FIX
echo ========================================
echo.

REM Проверка Python
echo [INFO] Проверка Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python не найден!
    pause
    exit /b 1
)

REM Установка зависимостей
echo [INFO] Установка зависимостей...
pip install paramiko requests --quiet
if %errorlevel% neq 0 (
    echo [WARNING] Возможны предупреждения при установке, проверяем...
    pip list | findstr paramiko >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Не удалось установить зависимости
        pause
        exit /b 1
    )
)

REM Запуск специального фикса
echo [INFO] Запуск специального фикса для Toshiba HDWT860...
echo.
echo Этот фикс специально разработан для Toshiba HDWT860 5.5TB
echo и должен решить проблему с "Не распознано" (Unrecognized)
echo.
pause

python toshiba_hdwt860_fix.py

pause

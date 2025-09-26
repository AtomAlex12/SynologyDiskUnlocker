@echo off
REM Synology Drive Unlocker - Быстрый старт
REM Запуск упрощенной версии "из коробки"

REM ---------- Fix console encoding ----------
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

title Synology Drive Unlocker - Быстрый старт

echo.
echo ========================================
echo   Synology Drive Unlocker v1.0 (Quick Start)
echo ========================================
echo.

REM Проверка Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python не найден!
    echo Установите Python 3.7+ с https://python.org
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

REM Запуск упрощенной версии
echo [INFO] Запуск упрощенной версии...
echo.
python one_click_unlocker.py

pause

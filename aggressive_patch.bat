@echo off
REM Synology Drive Unlocker - Агрессивный патч
REM Максимально эффективный обход ограничений

REM ---------- Fix console encoding ----------
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

title Synology Drive Unlocker - Агрессивный патч

echo.
echo ========================================
echo   АГРЕССИВНЫЙ ПАТЧ Synology
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

REM Запуск агрессивного патча
echo [INFO] Запуск агрессивного патча...
echo.
echo ВНИМАНИЕ: Этот патч применяет максимально агрессивные методы!
echo Используйте только если обычные методы не сработали.
echo.
pause

python aggressive_patch.py

pause

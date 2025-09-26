@echo off
REM Synology Drive Unlocker PRO - Единое приложение
REM Красивое приложение со всеми патчами и продвинутой системой логирования

REM ---------- Fix console encoding ----------
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

title Synology Drive Unlocker PRO v2.0

echo.
echo ========================================
echo   Synology Drive Unlocker PRO v2.0
echo ========================================
echo.

REM Проверка Python
echo [INFO] Проверка Python...
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

REM Создание директорий
if not exist "logs" mkdir logs
if not exist "backups" mkdir backups

REM Запуск PRO версии
echo [INFO] Запуск Synology Drive Unlocker PRO...
echo.
echo ========================================
echo   Запуск единого приложения...
echo ========================================
echo.

python synology_unlocker_pro.py

REM Обработка завершения
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Приложение завершилось с ошибкой (код: %errorlevel%)
    echo.
) else (
    echo.
    echo [INFO] Приложение завершено успешно
    echo.
)

echo Нажмите любую клавишу для выхода...
pause >nul

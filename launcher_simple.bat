@echo off
REM Synology Drive Unlocker - Простой запуск без виртуального окружения
REM Для быстрого тестирования

REM ---------- Fix console encoding ----------
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

title Synology Drive Unlocker - Простой запуск

echo.
echo ========================================
echo   Synology Drive Unlocker v1.0 (Simple)
echo ========================================
echo.

REM Проверка Python
echo [INFO] Проверка Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python не найден! Установите Python 3.7+ с https://python.org
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

REM Проверка установки
echo [INFO] Проверка установки...
python test_install.py
if %errorlevel% neq 0 (
    echo [ERROR] Проверка зависимостей не прошла
    pause
    exit /b 1
)

REM Создание директорий
if not exist "backups" mkdir backups
if not exist "logs" mkdir logs

REM Запуск приложения
echo.
echo [INFO] Запуск Synology Drive Unlocker...
echo ========================================
echo.

python one_click_unlocker.py

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

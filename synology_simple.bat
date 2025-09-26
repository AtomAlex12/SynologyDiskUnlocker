@echo off
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

echo ========================================
echo Synology Drive Unlocker - Простая версия
echo ========================================
echo.

echo [INFO] Проверка Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python не найден! Установите Python 3.7+
    pause
    exit /b 1
)
echo [OK] Python найден

echo [INFO] Проверка pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pip не найден!
    pause
    exit /b 1
)
echo [OK] pip найден

echo [INFO] Проверка зависимостей...
pip list | findstr paramiko >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Установка зависимостей...
    pip install paramiko --quiet
    if %errorlevel% neq 0 (
        echo [ERROR] Не удалось установить paramiko
        pause
        exit /b 1
    )
    echo [OK] Зависимости установлены
) else (
    echo [OK] Зависимости уже установлены
)

echo [INFO] Запуск Synology Drive Unlocker - Простая версия...
echo.
python synology_unlocker_simple.py

if %errorlevel% neq 0 (
    echo [ERROR] Приложение завершилось с ошибкой (код: %errorlevel%)
) else (
    echo [INFO] Приложение завершено успешно
)

echo.
echo Нажмите любую клавишу для выхода...
pause >nul

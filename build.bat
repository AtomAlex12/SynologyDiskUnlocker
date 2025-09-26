@echo off
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

echo ========================================
echo Сборка Synology Drive Unlocker
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

echo [INFO] Запуск сборки...
python build_exe.py

if %errorlevel% neq 0 (
    echo [ERROR] Сборка завершилась с ошибкой (код: %errorlevel%)
) else (
    echo [INFO] Сборка завершена успешно
)

echo.
echo Нажмите любую клавишу для выхода...
pause >nul

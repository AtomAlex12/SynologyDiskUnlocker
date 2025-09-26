@echo off
REM Synology Drive Unlocker - Исправление зависимостей
REM Принудительная переустановка всех зависимостей

REM ---------- Fix console encoding ----------
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

title Synology Drive Unlocker - Исправление зависимостей

echo.
echo ========================================
echo   Исправление зависимостей
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

REM Активация виртуального окружения если есть
if exist "venv" (
    echo [INFO] Активация виртуального окружения...
    call venv\Scripts\activate.bat
)

REM Удаление старых зависимостей
echo [INFO] Очистка старых зависимостей...
pip uninstall paramiko requests -y >nul 2>&1

REM Установка зависимостей заново
echo [INFO] Установка зависимостей заново...
pip install paramiko requests --upgrade --force-reinstall

REM Проверка установки
echo [INFO] Проверка установки...
python test_install.py
if %errorlevel% neq 0 (
    echo [ERROR] Проверка не прошла, пробуем альтернативный способ...
    
    REM Альтернативная установка
    echo [INFO] Альтернативная установка...
    pip install --no-cache-dir paramiko requests
    
    REM Повторная проверка
    python test_install.py
    if %errorlevel% neq 0 (
        echo [ERROR] Не удалось исправить зависимости
        pause
        exit /b 1
    )
)

echo [OK] Зависимости исправлены успешно!
echo.
echo Теперь можно запустить основную утилиту:
echo   launcher.bat
echo   или
echo   launcher_simple.bat
echo.

pause

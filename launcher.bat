@echo off
REM Synology Drive Unlocker - Launcher для Windows
REM Автоматический запуск утилиты с проверкой зависимостей

REM ---------- Fix console encoding ----------
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

title Synology Drive Unlocker v1.0

echo.
echo ========================================
echo   Synology Drive Unlocker v1.0 (Launcher)
echo ========================================
echo.

REM Проверка наличия Python
echo [INFO] Проверка Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python не найден! Установите Python 3.7+ с https://python.org
    echo.
    pause
    exit /b 1
)

REM Получение версии Python
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% найден

REM Проверка pip
echo [INFO] Проверка pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pip не найден! Переустановите Python с опцией pip
    echo.
    pause
    exit /b 1
)
echo [OK] pip найден

REM Проверка виртуального окружения
if not exist "venv" (
    echo [INFO] Создание виртуального окружения...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Не удалось создать виртуальное окружение
        pause
        exit /b 1
    )
    echo [OK] Виртуальное окружение создано
)

REM Активация виртуального окружения
echo [INFO] Активация виртуального окружения...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Не удалось активировать виртуальное окружение
    pause
    exit /b 1
)

REM Проверка и установка зависимостей
echo [INFO] Проверка зависимостей...
pip list | findstr paramiko >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Установка зависимостей...
    pip install -r requirements.txt --quiet
    if %errorlevel% neq 0 (
        echo [WARNING] Возможны предупреждения при установке, проверяем...
        pip list | findstr paramiko >nul 2>&1
        if %errorlevel% neq 0 (
            echo [ERROR] Не удалось установить зависимости
            pause
            exit /b 1
        )
    )
    echo [OK] Зависимости установлены
) else (
    echo [INFO] Проверяем все необходимые модули...
    pip list | findstr requests >nul 2>&1
    if %errorlevel% neq 0 (
        echo [INFO] Устанавливаем недостающие модули...
        pip install requests --quiet
    )
    echo [OK] Зависимости уже установлены
)

REM Проверка установки
echo [INFO] Проверка установки...
python test_install.py
if %errorlevel% neq 0 (
    echo [ERROR] Проверка зависимостей не прошла
    pause
    exit /b 1
)
echo [OK] Проверка зависимостей прошла успешно

REM Проверка основного файла
if not exist "synology_unlocker.py" (
    echo [ERROR] Файл synology_unlocker.py не найден!
    echo Убедитесь, что вы находитесь в правильной директории
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

python synology_unlocker.py

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

REM Пауза перед закрытием
echo Нажмите любую клавишу для выхода...
pause >nul

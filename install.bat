@echo off
REM Synology Drive Unlocker - Установщик для Windows
REM Автоматическая установка и настройка утилиты

REM ---------- Fix console encoding ----------
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

title Synology Drive Unlocker - Установщик

echo.
echo ========================================
echo   Synology Drive Unlocker v1.0 (Install)
echo ========================================
echo.

REM Проверка прав администратора
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Рекомендуется запустить от имени администратора
    echo.
)

REM Проверка наличия Python
echo [INFO] Проверка Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python не найден!
    echo.
    echo Установите Python 3.7+ с https://python.org
    echo Обязательно отметьте "Add Python to PATH" при установке
    echo.
    pause
    exit /b 1
)

REM Получение версии Python
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% найден

REM Создание виртуального окружения
echo [INFO] Создание виртуального окружения...
if exist "venv" (
    echo [INFO] Виртуальное окружение уже существует, удаляем...
    rmdir /s /q venv
)

python -m venv venv
if %errorlevel% neq 0 (
    echo [ERROR] Не удалось создать виртуальное окружение
    pause
    exit /b 1
)
echo [OK] Виртуальное окружение создано

REM Активация виртуального окружения
echo [INFO] Активация виртуального окружения...
call venv\Scripts\activate.bat

REM Обновление pip
echo [INFO] Обновление pip...
python -m pip install --upgrade pip

REM Установка зависимостей
echo [INFO] Установка зависимостей...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Не удалось установить зависимости
    pause
    exit /b 1
)
echo [OK] Зависимости установлены

REM Создание директорий
echo [INFO] Создание необходимых директорий...
if not exist "backups" mkdir backups
if not exist "logs" mkdir logs
if not exist "scripts" mkdir scripts
echo [OK] Директории созданы

REM Создание ярлыка на рабочем столе
echo [INFO] Создание ярлыка на рабочем столе...
set DESKTOP=%USERPROFILE%\Desktop
set SHORTCUT_PATH=%DESKTOP%\Synology Drive Unlocker.lnk

powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT_PATH%'); $Shortcut.TargetPath = '%~dp0launcher.bat'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Description = 'Synology Drive Unlocker v1.0'; $Shortcut.Save()}" 2>nul

if exist "%SHORTCUT_PATH%" (
    echo [OK] Ярлык создан на рабочем столе
) else (
    echo [WARNING] Не удалось создать ярлык на рабочем столе
)

REM Создание файла конфигурации по умолчанию
echo [INFO] Создание конфигурации по умолчанию...
if not exist "config.json" (
    echo {> config.json
    echo   "ip": "192.168.1.100",>> config.json
    echo   "ssh_port": 22,>> config.json
    echo   "login": "admin">> config.json
    echo }>> config.json
    echo [OK] Конфигурация создана
)

REM Проверка установки
echo [INFO] Проверка установки...
python -c "import paramiko; print('paramiko OK')" 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Проверка зависимостей не прошла
    pause
    exit /b 1
)
echo [OK] Проверка зависимостей прошла успешно

REM Создание README для пользователя
echo [INFO] Создание инструкций для пользователя...
(
echo # Synology Drive Unlocker - Готов к использованию
echo.
echo ## Быстрый старт:
echo 1. Запустите launcher.bat или ярлык на рабочем столе
echo 2. Введите IP адрес вашего NAS
echo 3. Укажите логин и пароль администратора
echo 4. Нажмите "Проверить подключение"
echo 5. Нажмите "Разблокировать диски"
echo.
echo ## Важно:
echo - Убедитесь, что SSH включен на вашем NAS
echo - Используйте учетную запись с правами администратора
echo - Создайте резервную копию данных перед использованием
echo.
echo ## Поддержка:
echo - README.md - подробная документация
echo - logs/ - файлы логов
echo - backups/ - резервные копии
) > QUICK_START.txt

echo [OK] Инструкции созданы

echo.
echo ========================================
echo           УСТАНОВКА ЗАВЕРШЕНА
echo ========================================
echo.
echo [OK] Synology Drive Unlocker успешно установлен!
echo.
echo Способы запуска:
echo 1. Двойной клик по launcher.bat
echo 2. Ярлык на рабочем столе
echo 3. Запуск из командной строки: launcher.bat
echo.
echo Документация:
echo - README.md - полная документация
echo - QUICK_START.txt - быстрый старт
echo.
echo ВНИМАНИЕ: Используйте на свой страх и риск!
echo.

pause

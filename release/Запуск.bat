@echo off
chcp 65001 >nul
title Synology Drive Unlocker
echo ========================================
echo Synology Drive Unlocker - Простая версия
echo ========================================
echo.
echo Запуск приложения...
echo.
SynologyDriveUnlocker.exe
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Приложение завершилось с ошибкой
    pause
)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для сборки exe файла Synology Drive Unlocker
"""

import os
import sys
import subprocess
import shutil

def install_pyinstaller():
    """Установка PyInstaller"""
    print("📦 Установка PyInstaller...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✅ PyInstaller установлен")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка установки PyInstaller: {e}")
        return False

def build_exe():
    """Сборка exe файла"""
    print("🔨 Сборка exe файла...")
    
    # Команда PyInstaller
    cmd = [
        "pyinstaller",
        "--onefile",                    # Один exe файл
        "--windowed",                   # Без консоли
        "--name=SynologyDriveUnlocker", # Имя exe файла
        "--icon=icon.ico",              # Иконка (если есть)
        "--add-data=requirements_simple.txt;.",  # Добавить requirements
        "synology_unlocker_final.py"   # Исходный файл
    ]
    
    # Убираем иконку если файла нет
    if not os.path.exists("icon.ico"):
        cmd.remove("--icon=icon.ico")
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ Exe файл собран успешно!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка сборки: {e}")
        return False

def create_installer():
    """Создание установщика"""
    print("📦 Создание установщика...")
    
    # Создаем папку для релиза
    release_dir = "release"
    if os.path.exists(release_dir):
        shutil.rmtree(release_dir)
    os.makedirs(release_dir)
    
    # Копируем exe файл
    exe_path = "dist/SynologyDriveUnlocker.exe"
    if os.path.exists(exe_path):
        shutil.copy2(exe_path, f"{release_dir}/SynologyDriveUnlocker.exe")
        print("✅ Exe файл скопирован в release/")
    
    # Создаем README
    readme_content = """# Synology Drive Unlocker - Простая версия

## Описание
Утилита для разблокировки несовместимых дисков на Synology NAS.

## Использование
1. Запустите SynologyDriveUnlocker.exe
2. Введите IP адрес NAS, логин и пароль
3. Отметьте "Использовать sudo"
4. Нажмите "Проверить подключение"
5. Выберите нужный патч:
   - "Стандартный патч" - для любых дисков
   - "Toshiba HDWT860" - для дисков Toshiba HDWT860

## Требования
- Windows 7/8/10/11
- Python 3.7+ (встроен в exe)
- SSH доступ к NAS
- Права администратора на NAS

## Безопасность
- Все изменения создают резервные копии
- Рекомендуется перезагрузить NAS после применения патча

## Поддержка
- DSM 6.x и 7.x
- Модели: DS225+, DS224+, DS723+, DS923+
- Диски: любые, включая Toshiba HDWT860

## Автор
AtomAlex12
"""
    
    with open(f"{release_dir}/README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("✅ README создан")
    
    # Создаем батник для запуска
    bat_content = """@echo off
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
"""
    
    with open(f"{release_dir}/Запуск.bat", "w", encoding="utf-8") as f:
        f.write(bat_content)
    
    print("✅ Батник для запуска создан")
    
    # Создаем архив
    print("📦 Создание архива...")
    try:
        shutil.make_archive("SynologyDriveUnlocker_v1.0", "zip", release_dir)
        print("✅ Архив SynologyDriveUnlocker_v1.0.zip создан")
    except Exception as e:
        print(f"⚠️ Ошибка создания архива: {e}")

def main():
    """Основная функция"""
    print("🚀 Сборка Synology Drive Unlocker")
    print("=" * 50)
    
    # Проверяем наличие исходного файла
    if not os.path.exists("synology_unlocker_simple.py"):
        print("❌ Файл synology_unlocker_simple.py не найден!")
        return
    
    # Устанавливаем PyInstaller
    if not install_pyinstaller():
        return
    
    # Собираем exe
    if not build_exe():
        return
    
    # Создаем установщик
    create_installer()
    
    print("\n🎉 Сборка завершена!")
    print("📁 Файлы находятся в папке 'release/'")
    print("📦 Архив: SynologyDriveUnlocker_v1.0.zip")

if __name__ == "__main__":
    main()

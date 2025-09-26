#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Создание чистой версии проекта для распространения
"""

import os
import shutil
import re

def create_clean_release():
    """Создание чистой версии проекта"""
    print("🧹 Создание чистой версии проекта...")
    
    # Создаем папку для чистого релиза
    clean_dir = "SynologyDriveUnlocker_Clean"
    if os.path.exists(clean_dir):
        shutil.rmtree(clean_dir)
    os.makedirs(clean_dir)
    
    # Файлы для копирования
    files_to_copy = [
        "synology_unlocker_final.py",
        "synology_unlocker_simple.py", 
        "synology_unlocker_pro.py",
        "requirements.txt",
        "requirements_simple.txt",
        "build_exe.py",
        "create_icon.py",
        "build.bat",
        "synology_simple.bat",
        "synology_pro.bat",
        "install.bat",
        "launcher.bat",
        "README.md",
        "RELEASE_README.md",
        "icon.ico",
        "icon.png"
    ]
    
    # Копируем файлы
    for file_name in files_to_copy:
        if os.path.exists(file_name):
            shutil.copy2(file_name, clean_dir)
            print(f"✅ Скопирован: {file_name}")
    
    # Копируем папки
    dirs_to_copy = ["scripts", "release"]
    for dir_name in dirs_to_copy:
        if os.path.exists(dir_name):
            shutil.copytree(dir_name, os.path.join(clean_dir, dir_name))
            print(f"✅ Скопирована папка: {dir_name}")
    
    # Создаем .gitignore
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Config files with personal data
config*.json

# Build artifacts
*.spec
build/
dist/

# Temporary files
*.tmp
*.cache
"""
    
    with open(os.path.join(clean_dir, ".gitignore"), "w", encoding="utf-8") as f:
        f.write(gitignore_content)
    
    # Создаем README для разработчиков
    dev_readme = """# Synology Drive Unlocker - Исходный код

## Описание
Исходный код утилиты для разблокировки несовместимых дисков на Synology NAS.

## Структура проекта

### Основные файлы
- `synology_unlocker_final.py` - Финальная версия (для exe)
- `synology_unlocker_simple.py` - Простая версия
- `synology_unlocker_pro.py` - PRO версия с расширенными функциями

### Скрипты сборки
- `build_exe.py` - Сборка exe файла
- `create_icon.py` - Создание иконки
- `build.bat` - Батник для сборки

### Запуск
- `synology_simple.bat` - Запуск простой версии
- `synology_pro.bat` - Запуск PRO версии
- `install.bat` - Установка зависимостей

### Документация
- `README.md` - Основная документация
- `RELEASE_README.md` - Документация для релиза

## Требования для разработки

```bash
pip install -r requirements.txt
```

## Сборка exe

```bash
python build_exe.py
```

## Лицензия
MIT License

## Автор
Synology Drive Unlocker Team
"""
    
    with open(os.path.join(clean_dir, "README_DEV.md"), "w", encoding="utf-8") as f:
        f.write(dev_readme)
    
    # Создаем архив
    print("📦 Создание архива...")
    shutil.make_archive("SynologyDriveUnlocker_Source_v1.0", "zip", clean_dir)
    print("✅ Архив создан: SynologyDriveUnlocker_Source_v1.0.zip")
    
    print(f"✅ Чистая версия создана в папке: {clean_dir}")
    print("📦 Архив исходного кода: SynologyDriveUnlocker_Source_v1.0.zip")

if __name__ == "__main__":
    create_clean_release()

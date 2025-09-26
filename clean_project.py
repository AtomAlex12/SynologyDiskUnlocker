#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для очистки проекта от личных данных
"""

import os
import shutil
import re

def clean_project():
    """Очистка проекта от личных данных"""
    print("🧹 Очистка проекта от личных данных...")
    
    # Удаляем временные файлы
    temp_files = [
        '*.log',
        '*.tmp',
        '*.cache',
        'config*.json',
        '*.pyc',
        '__pycache__',
        '.pytest_cache',
        '*.spec'
    ]
    
    for pattern in temp_files:
        if '*' in pattern:
            # Используем glob для поиска файлов
            import glob
            for file in glob.glob(pattern):
                try:
                    if os.path.isfile(file):
                        os.remove(file)
                        print(f"✅ Удален файл: {file}")
                except:
                    pass
        else:
            try:
                if os.path.exists(pattern):
                    if os.path.isfile(pattern):
                        os.remove(pattern)
                    else:
                        shutil.rmtree(pattern)
                    print(f"✅ Удалена папка/файл: {pattern}")
            except:
                pass
    
    # Удаляем папки сборки
    build_dirs = ['build', 'dist', 'logs', '__pycache__']
    for dir_name in build_dirs:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"✅ Удалена папка: {dir_name}")
            except:
                pass
    
    # Очищаем файлы от личных данных
    files_to_clean = [
        'synology_unlocker_simple.py',
        'synology_unlocker_final.py',
        'synology_unlocker_pro.py'
    ]
    
    for file_name in files_to_clean:
        if os.path.exists(file_name):
            clean_file_content(file_name)
    
    print("✅ Проект очищен от личных данных!")

def clean_file_content(filename):
    """Очистка содержимого файла от личных данных"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Заменяем IP адреса на примеры
        content = re.sub(r'\b192\.168\.\d+\.\d+\b', '192.168.1.100', content)
        content = re.sub(r'\b10\.\d+\.\d+\.\d+\b', '192.168.1.100', content)
        content = re.sub(r'\b172\.\d+\.\d+\.\d+\b', '192.168.1.100', content)
        
        # Заменяем имена пользователей
        content = re.sub(r'\balex\b', 'admin', content, flags=re.IGNORECASE)
        content = re.sub(r'\bАлександр\b', 'User', content)
        
        # Заменяем пути пользователей
        content = re.sub(r'C:\\Users\\[^\\]+\\', 'C:\\Users\\User\\', content)
        content = re.sub(r'D:\\projekt\\[^\\]+\\', 'D:\\project\\NAS\\', content)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Очищен файл: {filename}")
        
    except Exception as e:
        print(f"⚠️ Ошибка очистки {filename}: {e}")

if __name__ == "__main__":
    clean_project()

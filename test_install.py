#!/usr/bin/env python3
"""
Тест установки зависимостей для Synology Drive Unlocker
"""

import sys

def test_imports():
    """Тестирование импорта всех необходимых модулей"""
    print("Тестирование импорта модулей...")
    
    try:
        import paramiko
        print("✓ paramiko импортирован успешно")
    except ImportError as e:
        print(f"✗ Ошибка импорта paramiko: {e}")
        return False
    
    try:
        import requests
        print("✓ requests импортирован успешно")
    except ImportError as e:
        print(f"✗ Ошибка импорта requests: {e}")
        return False
    
    try:
        import tkinter
        print("✓ tkinter импортирован успешно")
    except ImportError as e:
        print(f"✗ Ошибка импорта tkinter: {e}")
        return False
    
    try:
        import json
        print("✓ json импортирован успешно")
    except ImportError as e:
        print(f"✗ Ошибка импорта json: {e}")
        return False
    
    try:
        import threading
        print("✓ threading импортирован успешно")
    except ImportError as e:
        print(f"✗ Ошибка импорта threading: {e}")
        return False
    
    try:
        import subprocess
        print("✓ subprocess импортирован успешно")
    except ImportError as e:
        print(f"✗ Ошибка импорта subprocess: {e}")
        return False
    
    return True

def test_ssh_connection():
    """Тестирование SSH подключения"""
    print("\nТестирование SSH функциональности...")
    
    try:
        import paramiko
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print("✓ SSH клиент создан успешно")
        return True
    except Exception as e:
        print(f"✗ Ошибка создания SSH клиента: {e}")
        return False

def main():
    print("=" * 50)
    print("Synology Drive Unlocker - Тест установки")
    print("=" * 50)
    
    print(f"Python версия: {sys.version}")
    print(f"Python путь: {sys.executable}")
    
    # Тест импортов
    if not test_imports():
        print("\n❌ Тест импортов не пройден!")
        return False
    
    # Тест SSH
    if not test_ssh_connection():
        print("\n❌ Тест SSH не пройден!")
        return False
    
    print("\n✅ Все тесты пройдены успешно!")
    print("Утилита готова к использованию.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

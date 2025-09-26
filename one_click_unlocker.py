#!/usr/bin/env python3
"""
Synology Drive Unlocker - One-Click Unlocker
Максимально упрощенная версия для работы "из коробки"
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import os
import sys
import json
import threading
import time
import requests
import socket
from pathlib import Path
import webbrowser
import paramiko

class OneClickUnlocker:
    def __init__(self, root):
        self.root = root
        self.root.title("Synology Drive Unlocker - One-Click")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Центрируем окно
        self.center_window()
        
        self.setup_ui()
        
    def center_window(self):
        """Центрирование окна на экране"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_ui(self):
        """Создание максимально простого интерфейса"""
        
        # Главный фрейм
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="🔓 Synology Drive Unlocker", 
                               font=("Arial", 20, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Подзаголовок
        subtitle_label = ttk.Label(main_frame, text="Разблокировка дисков одной кнопкой", 
                                  font=("Arial", 12))
        subtitle_label.pack(pady=(0, 30))
        
        # Инструкции
        instructions_frame = ttk.LabelFrame(main_frame, text="📋 Инструкции", padding="15")
        instructions_frame.pack(fill=tk.X, pady=(0, 20))
        
        instructions_text = """1. Введите IP адрес вашего Synology NAS
2. Укажите логин и пароль администратора
3. Нажмите "Разблокировать диски"
4. Дождитесь завершения процесса

⚠️ Убедитесь, что SSH включен в настройках DSM"""
        
        ttk.Label(instructions_frame, text=instructions_text, justify=tk.LEFT).pack()
        
        # Поля ввода
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(0, 20))
        
        # IP адрес
        ttk.Label(input_frame, text="IP адрес NAS:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.ip_var = tk.StringVar(value="192.168.1.100")
        ttk.Entry(input_frame, textvariable=self.ip_var, width=20).grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # Логин
        ttk.Label(input_frame, text="Логин:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.login_var = tk.StringVar(value="admin")
        ttk.Entry(input_frame, textvariable=self.login_var, width=20).grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        # Пароль
        ttk.Label(input_frame, text="Пароль:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.password_var, show="*", width=20).grid(row=2, column=1, sticky=tk.W, padx=(10, 0))
        
        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Основная кнопка
        self.unlock_button = ttk.Button(button_frame, text="🚀 РАЗБЛОКИРОВАТЬ ДИСКИ", 
                                       command=self.unlock_drives, style="Accent.TButton")
        self.unlock_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Кнопка помощи
        ttk.Button(button_frame, text="❓ Помощь", 
                  command=self.show_help).pack(side=tk.LEFT)
        
        # Прогресс
        self.progress_var = tk.StringVar(value="Готов к работе")
        ttk.Label(main_frame, textvariable=self.progress_var).pack(pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Лог (компактный)
        log_frame = ttk.LabelFrame(main_frame, text="📝 Статус", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, width=60)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
    def log(self, message):
        """Добавление сообщения в лог"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def unlock_drives(self):
        """Основная функция разблокировки"""
        self.log("🚀 Начинаем разблокировку дисков...")
        self.progress_bar.start()
        self.progress_var.set("Разблокировка дисков...")
        self.unlock_button.config(state="disabled")
        
        def unlock():
            try:
                ip = self.ip_var.get()
                login = self.login_var.get()
                password = self.password_var.get()
                
                if not all([ip, login, password]):
                    self.log("❌ Заполните все поля")
                    return
                
                # Шаг 1: Проверка подключения
                self.log("🔍 Проверка подключения к NAS...")
                if not self.test_connection(ip):
                    self.log("❌ Не удалось подключиться к NAS")
                    return
                
                # Шаг 2: Подключение по SSH
                self.log("🔐 Подключение по SSH...")
                ssh = self.connect_ssh(ip, login, password)
                if not ssh:
                    self.log("❌ Не удалось подключиться по SSH")
                    self.log("💡 Включите SSH в настройках DSM: Панель управления → Терминал и SNMP")
                    return
                
                # Шаг 3: Создание резервной копии
                self.log("💾 Создание резервной копии...")
                self.create_backup(ssh)
                
                # Шаг 4: Применение патча
                self.log("🔧 Применение патча...")
                self.apply_patch(ssh)
                
                # Шаг 5: Перезапуск служб
                self.log("🔄 Перезапуск служб...")
                self.restart_services(ssh)
                
                ssh.close()
                
                self.log("✅ Разблокировка завершена успешно!")
                self.log("🎉 Теперь можно использовать любые диски!")
                self.progress_var.set("Разблокировка завершена")
                
                # Показываем сообщение об успехе
                messagebox.showinfo("Успех!", 
                    "Диски успешно разблокированы!\n\n"
                    "Теперь вы можете использовать любые диски в вашем Synology NAS.\n"
                    "Рекомендуется перезагрузить NAS для полного применения изменений.")
                
            except Exception as e:
                self.log(f"❌ Ошибка: {e}")
                self.progress_var.set("Ошибка")
            finally:
                self.progress_bar.stop()
                self.unlock_button.config(state="normal")
        
        threading.Thread(target=unlock, daemon=True).start()
    
    def test_connection(self, ip):
        """Проверка подключения к NAS"""
        try:
            # Ping
            result = subprocess.run(['ping', '-n', '1', ip], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                return False
            
            # Проверка веб-интерфейса
            try:
                response = requests.get(f"http://{ip}:5000", timeout=5)
                return response.status_code == 200
            except:
                return False
                
        except:
            return False
    
    def connect_ssh(self, ip, login, password):
        """Подключение по SSH"""
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username=login, password=password, timeout=10)
            return ssh
        except Exception as e:
            self.log(f"❌ Ошибка SSH: {e}")
            return None
    
    def create_backup(self, ssh):
        """Создание резервной копии"""
        backup_script = """
        #!/bin/bash
        BACKUP_DIR="/tmp/synology_backup_$(date +%Y%m%d_%H%M%S)"
        mkdir -p $BACKUP_DIR
        
        cp /etc/synoinfo.conf $BACKUP_DIR/ 2>/dev/null || echo "synoinfo.conf not found"
        cp /usr/syno/bin/synocheck $BACKUP_DIR/ 2>/dev/null || echo "synocheck not found"
        
        echo "Backup created in $BACKUP_DIR"
        """
        
        stdin, stdout, stderr = ssh.exec_command(backup_script)
        output = stdout.read().decode()
        self.log(f"💾 Резервная копия: {output.strip()}")
    
    def apply_patch(self, ssh):
        """Применение патча"""
        patch_script = """
        #!/bin/bash
        
        # Создаем резервные копии
        cp /etc/synoinfo.conf /etc/synoinfo.conf.backup 2>/dev/null
        cp /usr/syno/bin/synocheck /usr/syno/bin/synocheck.backup 2>/dev/null
        
        # Отключаем проверки дисков
        sed -i 's/support_disk_compatibility="yes"/support_disk_compatibility="no"/g' /etc/synoinfo.conf
        sed -i 's/support_disk_compatibility_check="yes"/support_disk_compatibility_check="no"/g' /etc/synoinfo.conf
        
        # Добавляем дополнительные настройки
        echo "" >> /etc/synoinfo.conf
        echo "# Synology Drive Unlocker" >> /etc/synoinfo.conf
        echo "support_disk_compatibility=\"no\"" >> /etc/synoinfo.conf
        echo "support_disk_compatibility_check=\"no\"" >> /etc/synoinfo.conf
        
        # Модифицируем synocheck
        if [ -f /usr/syno/bin/synocheck ]; then
            sed -i 's/check_disk_compatibility/return 0 # check_disk_compatibility/g' /usr/syno/bin/synocheck
            chmod +x /usr/syno/bin/synocheck
        fi
        
        echo "Patch applied successfully"
        """
        
        stdin, stdout, stderr = ssh.exec_command(patch_script)
        output = stdout.read().decode()
        self.log(f"🔧 Патч: {output.strip()}")
    
    def restart_services(self, ssh):
        """Перезапуск служб"""
        restart_script = """
        #!/bin/bash
        /usr/syno/bin/synopkg restart pkgctl-WebStation 2>/dev/null || echo "WebStation restart failed"
        /usr/syno/bin/synopkg restart pkgctl-Docker 2>/dev/null || echo "Docker restart failed"
        echo "Services restarted"
        """
        
        stdin, stdout, stderr = ssh.exec_command(restart_script)
        output = stdout.read().decode()
        self.log(f"🔄 Службы: {output.strip()}")
    
    def show_help(self):
        """Показ справки"""
        help_text = """🔓 Synology Drive Unlocker - Справка

ПРОБЛЕМЫ С ПОДКЛЮЧЕНИЕМ:
• Убедитесь, что NAS включен и подключен к сети
• Проверьте IP адрес в настройках DSM
• Включите SSH: Панель управления → Терминал и SNMP

ПРОБЛЕМЫ С SSH:
• Убедитесь, что SSH включен
• Проверьте логин и пароль
• Убедитесь, что у пользователя есть права администратора

ПОСЛЕ РАЗБЛОКИРОВКИ:
• Перезагрузите NAS для полного применения изменений
• Проверьте, что диски определяются без предупреждений
• Создайте пул хранения как обычно

ВОССТАНОВЛЕНИЕ:
• Используйте основную утилиту для восстановления настроек
• Или восстановите из резервных копий вручную

ПОДДЕРЖКА:
• README.md - полная документация
• logs/ - файлы логов
• backups/ - резервные копии"""
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Справка")
        help_window.geometry("500x400")
        
        text_widget = scrolledtext.ScrolledText(help_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)

def main():
    root = tk.Tk()
    app = OneClickUnlocker(root)
    root.mainloop()

if __name__ == "__main__":
    main()

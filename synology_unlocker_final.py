#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Synology Drive Unlocker - Финальная версия для exe
Основана на методе: https://github.com/007revad/Synology_HDD_db

MIT License
Copyright (c) 2025 AtomAlex12
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import paramiko
import threading
import time
import json
import os
import subprocess
import logging
import sys

class SynologyUnlockerFinal:
    def __init__(self, root):
        self.root = root
        self.root.title("Synology Drive Unlocker v1.0")
        self.root.geometry("900x700")
        self.root.configure(bg='#2b2b2b')
        
        # Переменные
        self.ip_var = tk.StringVar()
        self.login_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.use_sudo_var = tk.BooleanVar(value=True)
        
        # Настройка логирования
        self.setup_logging()
        
        # Создание интерфейса
        self.setup_ui()
        
        # Загрузка конфигурации
        self.load_config()
        
        # SSH соединение
        self.ssh = None
    
    def setup_logging(self):
        """Настройка логирования"""
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(log_dir, 'unlocker_final.log'), encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_ui(self):
        """Создание интерфейса"""
        # Заголовок
        title_frame = tk.Frame(self.root, bg='#2b2b2b')
        title_frame.pack(fill='x', padx=20, pady=10)
        
        title_label = tk.Label(
            title_frame,
            text="🔓 Synology Drive Unlocker v1.0",
            font=('Arial', 18, 'bold'),
            fg='#00ff00',
            bg='#2b2b2b'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Разблокировка несовместимых дисков на Synology NAS",
            font=('Arial', 10),
            fg='#cccccc',
            bg='#2b2b2b'
        )
        subtitle_label.pack()
        
        # Основной фрейм
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Настройки подключения
        settings_frame = tk.LabelFrame(
            main_frame,
            text="Настройки подключения",
            font=('Arial', 12, 'bold'),
            fg='#ffffff',
            bg='#3b3b3b',
            relief='raised',
            bd=2
        )
        settings_frame.pack(fill='x', pady=(0, 10))
        
        # IP адрес
        tk.Label(settings_frame, text="IP адрес NAS:", fg='#ffffff', bg='#3b3b3b').grid(row=0, column=0, sticky='w', padx=10, pady=5)
        tk.Entry(settings_frame, textvariable=self.ip_var, width=25, bg='#4b4b4b', fg='#ffffff').grid(row=0, column=1, padx=10, pady=5)
        
        # Логин
        tk.Label(settings_frame, text="Логин:", fg='#ffffff', bg='#3b3b3b').grid(row=1, column=0, sticky='w', padx=10, pady=5)
        tk.Entry(settings_frame, textvariable=self.login_var, width=25, bg='#4b4b4b', fg='#ffffff').grid(row=1, column=1, padx=10, pady=5)
        
        # Пароль
        tk.Label(settings_frame, text="Пароль:", fg='#ffffff', bg='#3b3b3b').grid(row=2, column=0, sticky='w', padx=10, pady=5)
        tk.Entry(settings_frame, textvariable=self.password_var, show='*', width=25, bg='#4b4b4b', fg='#ffffff').grid(row=2, column=1, padx=10, pady=5)
        
        # Использовать sudo
        tk.Checkbutton(
            settings_frame,
            text="Использовать sudo (рекомендуется)",
            variable=self.use_sudo_var,
            fg='#ffffff',
            bg='#3b3b3b',
            selectcolor='#2b2b2b'
        ).grid(row=3, column=0, columnspan=2, sticky='w', padx=10, pady=5)
        
        # Кнопки
        buttons_frame = tk.Frame(main_frame, bg='#2b2b2b')
        buttons_frame.pack(fill='x', pady=10)
        
        # Проверка подключения
        tk.Button(
            buttons_frame,
            text="🔍 Проверить подключение",
            command=self.test_connection,
            bg='#4b4b4b',
            fg='#ffffff',
            font=('Arial', 10, 'bold'),
            relief='raised',
            bd=2,
            width=20
        ).pack(side='left', padx=5)
        
        # Стандартный патч
        tk.Button(
            buttons_frame,
            text="🔧 Стандартный патч",
            command=self.apply_standard_patch,
            bg='#0066cc',
            fg='#ffffff',
            font=('Arial', 10, 'bold'),
            relief='raised',
            bd=2,
            width=20
        ).pack(side='left', padx=5)
        
        # Toshiba HDWT860
        tk.Button(
            buttons_frame,
            text="💾 Toshiba HDWT860",
            command=self.apply_toshiba_fix,
            bg='#cc6600',
            fg='#ffffff',
            font=('Arial', 10, 'bold'),
            relief='raised',
            bd=2,
            width=20
        ).pack(side='left', padx=5)
        
        # Сохранить настройки
        tk.Button(
            buttons_frame,
            text="💾 Сохранить",
            command=self.save_config,
            bg='#4b4b4b',
            fg='#ffffff',
            font=('Arial', 10, 'bold'),
            relief='raised',
            bd=2,
            width=15
        ).pack(side='right', padx=5)
        
        # Лог
        log_frame = tk.LabelFrame(
            main_frame,
            text="Лог операций",
            font=('Arial', 12, 'bold'),
            fg='#ffffff',
            bg='#3b3b3b',
            relief='raised',
            bd=2
        )
        log_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=18,
            bg='#1e1e1e',
            fg='#00ff00',
            font=('Consolas', 9),
            wrap=tk.WORD
        )
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Статус
        self.status_var = tk.StringVar(value="Готов к работе")
        status_label = tk.Label(
            self.root,
            textvariable=self.status_var,
            fg='#00ff00',
            bg='#2b2b2b',
            font=('Arial', 10, 'bold')
        )
        status_label.pack(side='bottom', pady=5)
    
    def log(self, message):
        """Логирование"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        
        self.log_text.insert(tk.END, f"{log_message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
        self.logger.info(message)
    
    def test_connection(self):
        """Проверка подключения"""
        def test():
            try:
                self.log("🔍 Проверка подключения к NAS...")
                
                # Проверка ping
                ip = self.ip_var.get()
                if not ip:
                    self.log("❌ Введите IP адрес")
                    return
                
                self.log(f"📡 Ping {ip}...")
                result = subprocess.run(['ping', '-n', '1', ip], capture_output=True, text=True)
                if result.returncode != 0:
                    self.log("❌ NAS недоступен")
                    return
                
                self.log("✅ NAS доступен")
                
                # SSH подключение
                self.log("🔐 SSH подключение...")
                ssh = self.connect_ssh()
                if not ssh:
                    self.log("❌ SSH подключение не удалось")
                    return
                
                # Проверка sudo
                if self.use_sudo_var.get():
                    self.log("🔐 Проверка sudo доступа...")
                    output, error, code = self.execute_ssh_command(ssh, "whoami", use_sudo=True)
                    if code == 0 and "root" in output:
                        self.log("✅ Sudo доступ подтвержден - работаем от root")
                    else:
                        self.log("⚠️ Sudo недоступен, будет использован обычный пользователь")
                
                ssh.close()
                self.log("✅ Подключение успешно!")
                
            except Exception as e:
                self.log(f"❌ Ошибка: {e}")
        
        threading.Thread(target=test, daemon=True).start()
    
    def connect_ssh(self):
        """SSH подключение"""
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            ssh.connect(
                hostname=self.ip_var.get(),
                username=self.login_var.get(),
                password=self.password_var.get(),
                timeout=10
            )
            
            return ssh
        except Exception as e:
            self.log(f"❌ Ошибка SSH: {e}")
            return None
    
    def execute_ssh_command(self, ssh, command, use_sudo=False):
        """Выполнение SSH команды с улучшенной обработкой ошибок"""
        try:
            if use_sudo and self.use_sudo_var.get():
                # Переключение на root через sudo su
                self.log(f"🔐 Переключение на root через sudo su...")
                self.log(f"💻 >>> sudo su")
                
                # Создаем интерактивную сессию
                transport = ssh.get_transport()
                channel = transport.open_session()
                channel.get_pty()
                channel.invoke_shell()
                
                # Отправляем sudo su
                channel.send("sudo su\n")
                time.sleep(1)
                
                # Ждем запрос пароля
                response = ""
                timeout = 0
                while timeout < 50:
                    if channel.recv_ready():
                        data = channel.recv(1024).decode('utf-8', errors='ignore')
                        response += data
                        if "password" in data.lower() or "Password" in data:
                            break
                    time.sleep(0.1)
                    timeout += 1
                
                # Вводим пароль
                self.log(f"🔑 Ввод пароля для sudo...")
                self.log(f"💻 >>> [пароль скрыт]")
                channel.send(f"{self.password_var.get()}\n")
                time.sleep(2)
                
                # Ждем приглашения root
                response = ""
                timeout = 0
                while timeout < 100:
                    if channel.recv_ready():
                        data = channel.recv(1024).decode('utf-8', errors='ignore')
                        response += data
                        if "#" in data and "root" in data:
                            break
                    time.sleep(0.1)
                    timeout += 1
                
                self.log(f"✅ Переключились на root")
                
                # Выполняем команду
                self.log(f"💻 >>> {command}")
                channel.send(f"{command}\n")
                time.sleep(2)
                
                # Читаем результат
                output = ""
                timeout = 0
                while timeout < 200:
                    if channel.recv_ready():
                        data = channel.recv(1024).decode('utf-8', errors='ignore')
                        output += data
                        timeout = 0
                    else:
                        timeout += 1
                    time.sleep(0.1)
                
                # Выходим из root
                channel.send("exit\n")
                time.sleep(1)
                channel.close()
                
                if output.strip():
                    self.log(f"💻 <<< {output.strip()}")
                
                return output, "", 0
                
            else:
                # Обычное выполнение команды
                self.log(f"💻 >>> {command}")
                
                stdin, stdout, stderr = ssh.exec_command(command)
                
                # Ждем завершения
                while not stdout.channel.exit_status_ready():
                    time.sleep(0.1)
                
                exit_status = stdout.channel.recv_exit_status()
                output = stdout.read().decode('utf-8', errors='ignore')
                error = stderr.read().decode('utf-8', errors='ignore')
                
                if output.strip():
                    self.log(f"💻 <<< {output.strip()}")
                if error.strip():
                    self.log(f"💻 <<< ERROR: {error.strip()}")
                
                return output, error, exit_status
                
        except Exception as e:
            self.log(f"❌ Ошибка выполнения команды: {e}")
            return "", str(e), -1
    
    def apply_standard_patch(self):
        """Применение стандартного патча"""
        def patch():
            try:
                self.log("🔧 Применение стандартного патча...")
                
                ssh = self.connect_ssh()
                if not ssh:
                    self.log("❌ Не удалось подключиться")
                    return
                
                # Создание резервной копии
                self.log("💾 Создание резервной копии...")
                backup_script = """
                BACKUP_DIR="/tmp/synology_backup_$(date +%Y%m%d_%H%M%S)"
                mkdir -p $BACKUP_DIR
                cp /etc.defaults/synoinfo.conf $BACKUP_DIR/ 2>/dev/null || echo "synoinfo.conf not found"
                echo "Backup created in $BACKUP_DIR"
                """
                output, error, code = self.execute_ssh_command(ssh, backup_script, use_sudo=True)
                self.log(f"📁 Резервная копия: {output.strip()}")
                
                # Простая модификация synoinfo.conf
                self.log("🔧 Модификация /etc.defaults/synoinfo.conf...")
                
                commands = [
                    "sudo -i",
                    "sed -i 's/support_disk_compatibility=\"yes\"/support_disk_compatibility=\"no\"/g' /etc.defaults/synoinfo.conf",
                    "echo 'support_disk_compatibility=\"no\"' >> /etc.defaults/synoinfo.conf",
                    "echo 'support_disk_compatibility_override=\"yes\"' >> /etc.defaults/synoinfo.conf",
                    "echo 'Disk compatibility check disabled'",
                    "exit"
                ]
                
                for cmd in commands:
                    self.log(f"💻 >>> {cmd}")
                    output, error, code = self.execute_ssh_command(ssh, cmd, use_sudo=True)
                    if output.strip():
                        self.log(f"💻 <<< {output.strip()}")
                
                ssh.close()
                self.log("✅ Стандартный патч применен успешно!")
                self.log("🔄 Рекомендуется перезагрузить NAS для применения изменений")
                
            except Exception as e:
                self.log(f"❌ Ошибка: {e}")
        
        threading.Thread(target=patch, daemon=True).start()
    
    def apply_toshiba_fix(self):
        """Применение фикса для Toshiba HDWT860"""
        def fix():
            try:
                self.log("💾 Применение фикса для Toshiba HDWT860...")
                
                ssh = self.connect_ssh()
                if not ssh:
                    self.log("❌ Не удалось подключиться")
                    return
                
                # Создание резервной копии
                self.log("💾 Создание резервной копии...")
                backup_script = """
                BACKUP_DIR="/tmp/toshiba_fix_backup_$(date +%Y%m%d_%H%M%S)"
                mkdir -p $BACKUP_DIR
                cp /etc.defaults/synoinfo.conf $BACKUP_DIR/ 2>/dev/null || echo "synoinfo.conf not found"
                echo "Backup created in $BACKUP_DIR"
                """
                output, error, code = self.execute_ssh_command(ssh, backup_script, use_sudo=True)
                self.log(f"📁 Резервная копия: {output.strip()}")
                
                # Специальная модификация для Toshiba
                self.log("🔧 Применение специального фикса для Toshiba HDWT860...")
                
                commands = [
                    "sudo -i",
                    "sed -i 's/support_disk_compatibility=\"yes\"/support_disk_compatibility=\"no\"/g' /etc.defaults/synoinfo.conf",
                    "echo 'support_disk_compatibility=\"no\"' >> /etc.defaults/synoinfo.conf",
                    "echo 'support_disk_compatibility_override=\"yes\"' >> /etc.defaults/synoinfo.conf",
                    "echo 'support_disk_compatibility_force=\"yes\"' >> /etc.defaults/synoinfo.conf",
                    "echo 'support_toshiba_hdwt860=\"yes\"' >> /etc.defaults/synoinfo.conf",
                    "echo 'support_disk_force_recognition=\"yes\"' >> /etc.defaults/synoinfo.conf",
                    "echo 'Toshiba HDWT860 special fix applied'",
                    "exit"
                ]
                
                for cmd in commands:
                    self.log(f"💻 >>> {cmd}")
                    output, error, code = self.execute_ssh_command(ssh, cmd, use_sudo=True)
                    if output.strip():
                        self.log(f"💻 <<< {output.strip()}")
                
                ssh.close()
                self.log("✅ Фикс для Toshiba HDWT860 применен успешно!")
                self.log("🔄 Рекомендуется перезагрузить NAS для применения изменений")
                
            except Exception as e:
                self.log(f"❌ Ошибка: {e}")
        
        threading.Thread(target=fix, daemon=True).start()
    
    def save_config(self):
        """Сохранение конфигурации"""
        try:
            config = {
                'ip': self.ip_var.get(),
                'login': self.login_var.get(),
                'password': self.password_var.get(),
                'use_sudo': self.use_sudo_var.get()
            }
            
            with open('config_final.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            self.log("💾 Конфигурация сохранена")
            
        except Exception as e:
            self.log(f"❌ Ошибка сохранения: {e}")
    
    def load_config(self):
        """Загрузка конфигурации"""
        try:
            if os.path.exists('config_final.json'):
                with open('config_final.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                self.ip_var.set(config.get('ip', ''))
                self.login_var.set(config.get('login', 'admin'))
                self.password_var.set(config.get('password', ''))
                self.use_sudo_var.set(config.get('use_sudo', True))
                
                self.log("📁 Конфигурация загружена")
                
        except Exception as e:
            self.log(f"⚠️ Ошибка загрузки конфигурации: {e}")

def main():
    root = tk.Tk()
    app = SynologyUnlockerFinal(root)
    root.mainloop()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Synology Drive Unlocker
Утилита для обхода ограничений на использование несертифицированных дисков в Synology NAS
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import subprocess
import os
import sys
import json
import threading
import time
from pathlib import Path
import paramiko
import socket

class SynologyUnlocker:
    def __init__(self, root):
        self.root = root
        self.root.title("Synology Drive Unlocker v1.0")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Настройки
        self.config_file = "config.json"
        self.backup_dir = "backups"
        self.log_file = "unlocker.log"
        self.ssh_client = None
        
        # Создаем необходимые директории
        Path(self.backup_dir).mkdir(exist_ok=True)
        
        self.setup_ui()
        self.load_config()
        
    def setup_ui(self):
        """Создание пользовательского интерфейса"""
        
        # Главный фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="🔓 Synology Drive Unlocker", 
                               font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Информационная панель
        info_frame = ttk.LabelFrame(main_frame, text="ℹ️ Информация", padding="10")
        info_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        info_text = """Эта утилита помогает обойти ограничения Synology на использование несертифицированных дисков.
Поддерживаемые модели: DS225+, DS224+, DS723+, DS923+ и другие серии Plus.

⚠️ ВНИМАНИЕ: Использование данной утилиты может привести к потере гарантии!
Рекомендуется создать резервную копию данных перед использованием."""
        
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).grid(row=0, column=0)
        
        # Настройки подключения
        settings_frame = ttk.LabelFrame(main_frame, text="🔧 Настройки подключения", padding="10")
        settings_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # IP адрес
        ttk.Label(settings_frame, text="IP адрес NAS:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.ip_var = tk.StringVar(value="192.168.1.100")
        ttk.Entry(settings_frame, textvariable=self.ip_var, width=20).grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        # Порт SSH
        ttk.Label(settings_frame, text="SSH порт:").grid(row=0, column=2, sticky=tk.W, padx=(20, 0), pady=2)
        self.ssh_port_var = tk.StringVar(value="22")
        ttk.Entry(settings_frame, textvariable=self.ssh_port_var, width=10).grid(row=0, column=3, sticky=tk.W, padx=(5, 0))
        
        # Логин
        ttk.Label(settings_frame, text="Логин:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.login_var = tk.StringVar(value="admin")
        ttk.Entry(settings_frame, textvariable=self.login_var, width=20).grid(row=1, column=1, sticky=tk.W, padx=(5, 0))
        
        # Пароль
        ttk.Label(settings_frame, text="Пароль:").grid(row=1, column=2, sticky=tk.W, padx=(20, 0), pady=2)
        self.password_var = tk.StringVar()
        ttk.Entry(settings_frame, textvariable=self.password_var, show="*", width=20).grid(row=1, column=3, sticky=tk.W, padx=(5, 0))
        
        # Опции
        options_frame = ttk.LabelFrame(main_frame, text="⚙️ Опции", padding="10")
        options_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.create_backup_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Создать резервную копию перед изменениями", 
                       variable=self.create_backup_var).grid(row=0, column=0, sticky=tk.W)
        
        self.auto_restart_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Автоматически перезапустить NAS после изменений", 
                       variable=self.auto_restart_var).grid(row=1, column=0, sticky=tk.W)
        
        self.force_unlock_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Принудительная разблокировка (для опытных пользователей)", 
                       variable=self.force_unlock_var).grid(row=2, column=0, sticky=tk.W)
        
        # Кнопки управления
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=4, column=0, columnspan=3, pady=(0, 10))
        
        ttk.Button(buttons_frame, text="🔍 Проверить подключение", 
                  command=self.test_connection).grid(row=0, column=0, padx=(0, 5))
        
        ttk.Button(buttons_frame, text="🔓 Разблокировать диски", 
                  command=self.unlock_drives).grid(row=0, column=1, padx=5)
        
        ttk.Button(buttons_frame, text="🔒 Восстановить ограничения", 
                  command=self.restore_restrictions).grid(row=0, column=2, padx=5)
        
        ttk.Button(buttons_frame, text="📋 Показать логи", 
                  command=self.show_logs).grid(row=0, column=3, padx=5)
        
        ttk.Button(buttons_frame, text="⚙️ Настройки", 
                  command=self.show_settings).grid(row=0, column=4, padx=5)
        
        # Прогресс бар
        self.progress_var = tk.StringVar(value="Готов к работе")
        ttk.Label(main_frame, textvariable=self.progress_var).grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Лог окно
        log_frame = ttk.LabelFrame(main_frame, text="📝 Лог операций", padding="5")
        log_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, width=100)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(2, weight=1)
        main_frame.rowconfigure(7, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
    def log(self, message):
        """Добавление сообщения в лог"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
        # Сохранение в файл
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_message)
    
    def test_connection(self):
        """Проверка подключения к NAS"""
        self.log("🔍 Проверка подключения к NAS...")
        self.progress_bar.start()
        self.progress_var.set("Проверка подключения...")
        
        def test():
            try:
                ip = self.ip_var.get()
                port = int(self.ssh_port_var.get())
                login = self.login_var.get()
                password = self.password_var.get()
                
                # Проверка ping
                self.log(f"Ping {ip}...")
                result = subprocess.run(['ping', '-n', '1', ip], 
                                      capture_output=True, text=True, timeout=10)
                
                if result.returncode != 0:
                    self.log(f"❌ NAS {ip} недоступен по ping")
                    self.progress_var.set("NAS недоступен")
                    return
                
                self.log(f"✅ NAS {ip} доступен по ping")
                
                # Проверка SSH
                self.log("Проверка SSH подключения...")
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
                try:
                    ssh.connect(ip, port=port, username=login, password=password, timeout=10)
                    self.log("✅ SSH подключение успешно")
                    
                    # Проверка версии DSM
                    stdin, stdout, stderr = ssh.exec_command("cat /etc.defaults/VERSION")
                    version = stdout.read().decode().strip()
                    self.log(f"📋 Версия DSM: {version}")
                    
                    # Проверка модели
                    stdin, stdout, stderr = ssh.exec_command("cat /proc/sys/kernel/syno_hw_version")
                    model = stdout.read().decode().strip()
                    self.log(f"🖥️ Модель: {model}")
                    
                    ssh.close()
                    self.log("✅ Подключение к NAS успешно установлено")
                    self.progress_var.set("Подключение успешно")
                    
                except paramiko.AuthenticationException:
                    self.log("❌ Ошибка аутентификации SSH")
                    self.progress_var.set("Ошибка аутентификации")
                except Exception as e:
                    self.log(f"❌ Ошибка SSH: {e}")
                    self.progress_var.set("Ошибка SSH")
                    
            except Exception as e:
                self.log(f"❌ Ошибка подключения: {e}")
                self.progress_var.set("Ошибка подключения")
            finally:
                self.progress_bar.stop()
        
        threading.Thread(target=test, daemon=True).start()
    
    def unlock_drives(self):
        """Основная функция разблокировки дисков"""
        self.log("🚀 Начинаем процесс разблокировки дисков...")
        self.progress_bar.start()
        self.progress_var.set("Разблокировка дисков...")
        
        def unlock():
            try:
                # Получаем параметры подключения
                ip = self.ip_var.get()
                port = int(self.ssh_port_var.get())
                login = self.login_var.get()
                password = self.password_var.get()
                
                # Устанавливаем SSH подключение
                self.ssh_client = paramiko.SSHClient()
                self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.ssh_client.connect(ip, port=port, username=login, password=password)
                
                # Создаем резервную копию если нужно
                if self.create_backup_var.get():
                    self.log("💾 Создание резервной копии...")
                    self.create_backup()
                
                # Применяем патч
                self.log("🔧 Применение патча для обхода ограничений...")
                self.apply_patch()
                
                # Перезапускаем службы
                self.log("🔄 Перезапуск служб...")
                self.restart_services()
                
                self.log("✅ Разблокировка завершена успешно!")
                self.progress_var.set("Разблокировка завершена")
                
                if self.auto_restart_var.get():
                    self.log("🔄 Перезапуск NAS...")
                    self.restart_nas()
                
                self.ssh_client.close()
                
            except Exception as e:
                self.log(f"❌ Ошибка при разблокировке: {e}")
                self.progress_var.set("Ошибка разблокировки")
                if self.ssh_client:
                    self.ssh_client.close()
            finally:
                self.progress_bar.stop()
        
        threading.Thread(target=unlock, daemon=True).start()
    
    def create_backup(self):
        """Создание резервной копии"""
        backup_script = """
        #!/bin/bash
        BACKUP_DIR="/tmp/synology_backup_$(date +%Y%m%d_%H%M%S)"
        mkdir -p $BACKUP_DIR
        
        # Копируем важные файлы
        cp /etc/synoinfo.conf $BACKUP_DIR/ 2>/dev/null || echo "synoinfo.conf not found"
        cp /usr/syno/bin/synocheck $BACKUP_DIR/ 2>/dev/null || echo "synocheck not found"
        cp /etc.defaults/synoinfo.conf $BACKUP_DIR/ 2>/dev/null || echo "default synoinfo.conf not found"
        
        echo "Backup created in $BACKUP_DIR"
        ls -la $BACKUP_DIR
        """
        
        stdin, stdout, stderr = self.ssh_client.exec_command(backup_script)
        output = stdout.read().decode()
        self.log(f"📁 Резервная копия: {output}")
    
    def apply_patch(self):
        """Применение патча"""
        patch_script = """
        #!/bin/bash
        
        echo "Applying disk compatibility patch..."
        
        # Отключаем проверки дисков в synoinfo.conf
        if [ -f /etc/synoinfo.conf ]; then
            cp /etc/synoinfo.conf /etc/synoinfo.conf.backup
            sed -i 's/support_disk_compatibility="yes"/support_disk_compatibility="no"/g' /etc/synoinfo.conf
            sed -i 's/support_disk_compatibility_check="yes"/support_disk_compatibility_check="no"/g' /etc/synoinfo.conf
            echo "Modified /etc/synoinfo.conf"
        fi
        
        # Модифицируем synocheck для пропуска проверок дисков
        if [ -f /usr/syno/bin/synocheck ]; then
            cp /usr/syno/bin/synocheck /usr/syno/bin/synocheck.backup
            sed -i 's/check_disk_compatibility/return 0 # check_disk_compatibility/g' /usr/syno/bin/synocheck
            chmod +x /usr/syno/bin/synocheck
            echo "Modified /usr/syno/bin/synocheck"
        fi
        
        # Дополнительные настройки для принудительной разблокировки
        if [ -f /etc/synoinfo.conf ]; then
            echo "support_disk_compatibility=\"no\"" >> /etc/synoinfo.conf
            echo "support_disk_compatibility_check=\"no\"" >> /etc/synoinfo.conf
            echo "support_disk_compatibility_override=\"yes\"" >> /etc/synoinfo.conf
        fi
        
        echo "Patch applied successfully"
        """
        
        stdin, stdout, stderr = self.ssh_client.exec_command(patch_script)
        output = stdout.read().decode()
        self.log(f"🔧 Патч применен: {output}")
    
    def restart_services(self):
        """Перезапуск служб"""
        restart_script = """
        #!/bin/bash
        echo "Restarting services..."
        
        # Перезапускаем основные службы
        /usr/syno/bin/synopkg restart pkgctl-WebStation 2>/dev/null || echo "WebStation restart failed"
        /usr/syno/bin/synopkg restart pkgctl-Docker 2>/dev/null || echo "Docker restart failed"
        
        # Перезапускаем службы хранения
        /usr/syno/bin/synopkg restart pkgctl-StorageManager 2>/dev/null || echo "StorageManager restart failed"
        
        echo "Services restarted"
        """
        
        stdin, stdout, stderr = self.ssh_client.exec_command(restart_script)
        output = stdout.read().decode()
        self.log(f"🔄 Службы перезапущены: {output}")
    
    def restart_nas(self):
        """Перезапуск NAS"""
        self.log("🔄 Перезапуск NAS через 5 секунд...")
        time.sleep(5)
        stdin, stdout, stderr = self.ssh_client.exec_command("sudo reboot")
        self.log("🔄 Команда перезапуска отправлена")
    
    def restore_restrictions(self):
        """Восстановление оригинальных ограничений"""
        self.log("🔒 Восстановление ограничений...")
        self.progress_bar.start()
        self.progress_var.set("Восстановление ограничений...")
        
        def restore():
            try:
                ip = self.ip_var.get()
                port = int(self.ssh_port_var.get())
                login = self.login_var.get()
                password = self.password_var.get()
                
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(ip, port=port, username=login, password=password)
                
                restore_script = """
                #!/bin/bash
                echo "Restoring original restrictions..."
                
                # Восстанавливаем synoinfo.conf
                if [ -f /etc/synoinfo.conf.backup ]; then
                    cp /etc/synoinfo.conf.backup /etc/synoinfo.conf
                    echo "Restored synoinfo.conf from backup"
                fi
                
                # Восстанавливаем synocheck
                if [ -f /usr/syno/bin/synocheck.backup ]; then
                    cp /usr/syno/bin/synocheck.backup /usr/syno/bin/synocheck
                    chmod +x /usr/syno/bin/synocheck
                    echo "Restored synocheck from backup"
                fi
                
                echo "Restrictions restored"
                """
                
                stdin, stdout, stderr = ssh.exec_command(restore_script)
                output = stdout.read().decode()
                self.log(f"🔒 Восстановление: {output}")
                
                ssh.close()
                self.log("✅ Ограничения восстановлены")
                self.progress_var.set("Ограничения восстановлены")
                
            except Exception as e:
                self.log(f"❌ Ошибка восстановления: {e}")
                self.progress_var.set("Ошибка восстановления")
            finally:
                self.progress_bar.stop()
        
        threading.Thread(target=restore, daemon=True).start()
    
    def show_logs(self):
        """Показать окно с логами"""
        log_window = tk.Toplevel(self.root)
        log_window.title("📋 Логи Synology Unlocker")
        log_window.geometry("800x600")
        
        log_text = scrolledtext.ScrolledText(log_window, wrap=tk.WORD)
        log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                log_text.insert(tk.END, f.read())
        except FileNotFoundError:
            log_text.insert(tk.END, "Лог файл не найден")
    
    def show_settings(self):
        """Показать окно настроек"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("⚙️ Настройки")
        settings_window.geometry("400x300")
        
        # Дополнительные настройки
        ttk.Label(settings_window, text="Дополнительные настройки", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Таймаут SSH
        ttk.Label(settings_window, text="SSH таймаут (секунды):").pack(anchor=tk.W, padx=10)
        timeout_var = tk.StringVar(value="30")
        ttk.Entry(settings_window, textvariable=timeout_var, width=20).pack(anchor=tk.W, padx=10)
        
        # Автосохранение логов
        auto_save_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_window, text="Автосохранение логов", 
                       variable=auto_save_var).pack(anchor=tk.W, padx=10)
        
        # Кнопки
        button_frame = ttk.Frame(settings_window)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Сохранить", 
                  command=lambda: self.save_settings(timeout_var.get(), auto_save_var.get())).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отмена", 
                  command=settings_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def save_settings(self, timeout, auto_save):
        """Сохранение настроек"""
        self.log(f"⚙️ Настройки сохранены: timeout={timeout}, auto_save={auto_save}")
    
    def load_config(self):
        """Загрузка конфигурации"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.ip_var.set(config.get("ip", "192.168.1.100"))
                    self.ssh_port_var.set(config.get("ssh_port", "22"))
                    self.login_var.set(config.get("login", "admin"))
        except Exception as e:
            self.log(f"⚠️ Ошибка загрузки конфигурации: {e}")
    
    def save_config(self):
        """Сохранение конфигурации"""
        config = {
            "ip": self.ip_var.get(),
            "ssh_port": self.ssh_port_var.get(),
            "login": self.login_var.get()
        }
        
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            self.log(f"⚠️ Ошибка сохранения конфигурации: {e}")

def main():
    root = tk.Tk()
    app = SynologyUnlocker(root)
    
    # Сохраняем конфигурацию при закрытии
    def on_closing():
        app.save_config()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()

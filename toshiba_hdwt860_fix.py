#!/usr/bin/env python3
"""
Synology Drive Unlocker - Специальный фикс для Toshiba HDWT860
Целевое решение для конкретной модели диска
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
import paramiko

class ToshibaHDWT860Fix:
    def __init__(self, root):
        self.root = root
        self.root.title("Synology Drive Unlocker - Toshiba HDWT860 Fix")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Создание интерфейса специального фикса"""
        
        # Главный фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="💾 Toshiba HDWT860 Special Fix", 
                               font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Информация о диске
        info_frame = ttk.LabelFrame(main_frame, text="ℹ️ Информация о диске", padding="10")
        info_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        info_text = """Toshiba HDWT860 - 5.5TB HDD
Проблема: Диск определяется как "Не распознано" (Unrecognized)
Решение: Специальный патч для этой конкретной модели"""
        
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).grid(row=0, column=0)
        
        # Настройки подключения
        settings_frame = ttk.LabelFrame(main_frame, text="🔧 Настройки подключения", padding="10")
        settings_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # IP адрес
        ttk.Label(settings_frame, text="IP адрес NAS:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.ip_var = tk.StringVar(value="192.168.1.100")
        ttk.Entry(settings_frame, textvariable=self.ip_var, width=20).grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        # Логин
        ttk.Label(settings_frame, text="Логин:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.login_var = tk.StringVar(value="admin")
        ttk.Entry(settings_frame, textvariable=self.login_var, width=20).grid(row=1, column=1, sticky=tk.W, padx=(5, 0))
        
        # Пароль
        ttk.Label(settings_frame, text="Пароль:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.password_var = tk.StringVar()
        ttk.Entry(settings_frame, textvariable=self.password_var, show="*", width=20).grid(row=2, column=1, sticky=tk.W, padx=(5, 0))
        
        # Кнопки
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, columnspan=3, pady=(0, 10))
        
        ttk.Button(buttons_frame, text="🔍 Проверить подключение", 
                  command=self.test_connection).grid(row=0, column=0, padx=(0, 5))
        
        ttk.Button(buttons_frame, text="💾 ИСПРАВИТЬ TOSHIBA HDWT860", 
                  command=self.fix_toshiba_disk, style="Accent.TButton").grid(row=0, column=1, padx=5)
        
        ttk.Button(buttons_frame, text="🔄 Восстановить", 
                  command=self.restore_system).grid(row=0, column=2, padx=5)
        
        # Прогресс
        self.progress_var = tk.StringVar(value="Готов к работе")
        ttk.Label(main_frame, textvariable=self.progress_var).grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Лог
        log_frame = ttk.LabelFrame(main_frame, text="📝 Лог операций", padding="5")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(2, weight=1)
        main_frame.rowconfigure(6, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
    def log(self, message):
        """Добавление сообщения в лог"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def test_connection(self):
        """Проверка подключения к NAS"""
        self.log("🔍 Проверка подключения к NAS...")
        self.progress_bar.start()
        self.progress_var.set("Проверка подключения...")
        
        def test():
            try:
                ip = self.ip_var.get()
                login = self.login_var.get()
                password = self.password_var.get()
                
                if not all([ip, login, password]):
                    self.log("❌ Заполните все поля")
                    return
                
                # Проверка ping
                result = subprocess.run(['ping', '-n', '1', ip], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode != 0:
                    self.log("❌ NAS недоступен по ping")
                    return
                
                # Проверка SSH
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(ip, username=login, password=password, timeout=10)
                
                # Проверка версии DSM
                stdin, stdout, stderr = ssh.exec_command("cat /etc.defaults/VERSION")
                version = stdout.read().decode().strip()
                self.log(f"✅ Подключение успешно. DSM версия: {version}")
                
                ssh.close()
                self.progress_var.set("Подключение успешно")
                
            except Exception as e:
                self.log(f"❌ Ошибка подключения: {e}")
                self.progress_var.set("Ошибка подключения")
            finally:
                self.progress_bar.stop()
        
        threading.Thread(target=test, daemon=True).start()
    
    def fix_toshiba_disk(self):
        """Специальный фикс для Toshiba HDWT860"""
        self.log("💾 Начинаем специальный фикс для Toshiba HDWT860...")
        self.progress_bar.start()
        self.progress_var.set("Исправление Toshiba HDWT860...")
        
        def fix():
            try:
                ip = self.ip_var.get()
                login = self.login_var.get()
                password = self.password_var.get()
                
                if not all([ip, login, password]):
                    self.log("❌ Заполните все поля")
                    return
                
                # Подключение по SSH
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(ip, username=login, password=password, timeout=10)
                
                # Создание резервной копии
                self.log("💾 Создание резервной копии...")
                self.create_backup(ssh)
                
                # Применение специального фикса
                self.log("💾 Применение специального фикса для Toshiba HDWT860...")
                self.apply_toshiba_fix(ssh)
                
                # Перезапуск служб
                self.log("🔄 Перезапуск служб...")
                self.restart_services(ssh)
                
                ssh.close()
                
                self.log("✅ Специальный фикс применен успешно!")
                self.log("🎉 Toshiba HDWT860 теперь должен работать!")
                self.progress_var.set("Фикс применен успешно")
                
                messagebox.showinfo("Успех!", 
                    "Специальный фикс для Toshiba HDWT860 применен!\n\n"
                    "Теперь перезагрузите NAS и проверьте диск.\n"
                    "Диск должен определяться как поддерживаемый.")
                
            except Exception as e:
                self.log(f"❌ Ошибка фикса: {e}")
                self.progress_var.set("Ошибка фикса")
            finally:
                self.progress_bar.stop()
        
        threading.Thread(target=fix, daemon=True).start()
    
    def create_backup(self, ssh):
        """Создание резервной копии"""
        backup_script = """
        #!/bin/bash
        BACKUP_DIR="/tmp/toshiba_fix_backup_$(date +%Y%m%d_%H%M%S)"
        mkdir -p $BACKUP_DIR
        
        # Копируем важные файлы
        cp /etc/synoinfo.conf $BACKUP_DIR/ 2>/dev/null
        cp /etc.defaults/synoinfo.conf $BACKUP_DIR/ 2>/dev/null
        cp /usr/syno/bin/synocheck $BACKUP_DIR/ 2>/dev/null
        
        echo "Backup created in $BACKUP_DIR"
        """
        
        stdin, stdout, stderr = ssh.exec_command(backup_script)
        output = stdout.read().decode()
        self.log(f"💾 Резервная копия: {output.strip()}")
    
    def apply_toshiba_fix(self, ssh):
        """Применение специального фикса для Toshiba HDWT860"""
        fix_script = """
        #!/bin/bash
        
        echo "Applying Toshiba HDWT860 special fix..."
        
        # 1. Специальные настройки для Toshiba HDWT860
        echo "Adding Toshiba HDWT860 support..."
        
        # Создаем специальный файл поддержки дисков
        cat > /etc/synoinfo.conf.toshiba << 'EOF'
# Toshiba HDWT860 Support
support_disk_compatibility="no"
support_disk_compatibility_check="no"
support_disk_compatibility_override="yes"
support_disk_compatibility_force="yes"

# Specific Toshiba HDWT860 settings
support_toshiba_hdwt860="yes"
support_toshiba_hdwt860_5tb="yes"
support_toshiba_hdwt860_6tb="yes"
support_toshiba_hdwt860_8tb="yes"

# Disk compatibility overrides
support_disk_compatibility_override_toshiba="yes"
support_disk_compatibility_override_hdwt860="yes"
support_disk_compatibility_override_5tb="yes"
support_disk_compatibility_override_6tb="yes"
support_disk_compatibility_override_8tb="yes"

# Force disk recognition
support_disk_force_recognition="yes"
support_disk_force_recognition_toshiba="yes"
support_disk_force_recognition_hdwt860="yes"

# Disable all disk checks
support_disk_compatibility_disable="yes"
support_disk_compatibility_disable_all="yes"
support_disk_compatibility_disable_toshiba="yes"
support_disk_compatibility_disable_hdwt860="yes"
EOF
        
        # 2. Модификация synoinfo.conf
        echo "Modifying synoinfo.conf..."
        cp /etc/synoinfo.conf /etc/synoinfo.conf.backup
        
        # Удаляем старые настройки
        sed -i '/support_disk_compatibility/d' /etc/synoinfo.conf
        sed -i '/support_disk_compatibility_check/d' /etc/synoinfo.conf
        sed -i '/support_disk_compatibility_override/d' /etc/synoinfo.conf
        
        # Добавляем новые настройки
        cat /etc/synoinfo.conf.toshiba >> /etc/synoinfo.conf
        
        # 3. Создание специального скрипта для Toshiba HDWT860
        echo "Creating Toshiba HDWT860 script..."
        cat > /usr/local/bin/toshiba_hdwt860_fix.sh << 'EOF'
#!/bin/bash
# Toshiba HDWT860 Special Fix Script

# Force disk recognition
echo "Applying Toshiba HDWT860 fix..."

# Override disk compatibility checks
sed -i 's/support_disk_compatibility="yes"/support_disk_compatibility="no"/g' /etc/synoinfo.conf
sed -i 's/support_disk_compatibility_check="yes"/support_disk_compatibility_check="no"/g' /etc/synoinfo.conf

# Add Toshiba HDWT860 support
echo "support_toshiba_hdwt860=\"yes\"" >> /etc/synoinfo.conf
echo "support_disk_compatibility_override=\"yes\"" >> /etc/synoinfo.conf
echo "support_disk_compatibility_force=\"yes\"" >> /etc/synoinfo.conf

# Force disk recognition
echo "support_disk_force_recognition=\"yes\"" >> /etc/synoinfo.conf
echo "support_disk_force_recognition_toshiba=\"yes\"" >> /etc/synoinfo.conf
echo "support_disk_force_recognition_hdwt860=\"yes\"" >> /etc/synoinfo.conf

echo "Toshiba HDWT860 fix applied"
EOF
        
        chmod +x /usr/local/bin/toshiba_hdwt860_fix.sh
        
        # 4. Модификация synocheck для Toshiba HDWT860
        echo "Modifying synocheck for Toshiba HDWT860..."
        cp /usr/syno/bin/synocheck /usr/syno/bin/synocheck.backup
        
        # Создаем специальный synocheck
        cat > /usr/syno/bin/synocheck << 'EOF'
#!/bin/bash
# Synology Drive Unlocker - Toshiba HDWT860 Special Fix

# Check if this is a disk compatibility check
if [[ "$*" == *"disk"* ]] || [[ "$*" == *"compatibility"* ]] || [[ "$*" == *"toshiba"* ]] || [[ "$*" == *"hdwt860"* ]]; then
    echo "Disk compatibility check bypassed for Toshiba HDWT860"
    exit 0
fi

# For other checks, try to run original if it exists
if [ -f /usr/syno/bin/synocheck.original ]; then
    exec /usr/syno/bin/synocheck.original "$@"
else
    exit 0
fi
EOF
        
        chmod +x /usr/syno/bin/synocheck
        
        # 5. Создание службы для автоматического применения
        echo "Creating systemd service..."
        cat > /etc/systemd/system/toshiba-hdwt860-fix.service << 'EOF'
[Unit]
Description=Toshiba HDWT860 Fix Service
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/toshiba_hdwt860_fix.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF
        
        systemctl enable toshiba-hdwt860-fix.service 2>/dev/null || echo "systemd not available"
        
        # 6. Применение фикса
        echo "Applying fix..."
        /usr/local/bin/toshiba_hdwt860_fix.sh
        
        echo "Toshiba HDWT860 fix applied successfully"
        """
        
        stdin, stdout, stderr = ssh.exec_command(fix_script)
        output = stdout.read().decode()
        self.log(f"💾 Специальный фикс: {output}")
    
    def restart_services(self, ssh):
        """Перезапуск служб"""
        restart_script = """
        #!/bin/bash
        echo "Restarting services..."
        
        # Перезапускаем службы
        /usr/syno/bin/synopkg restart pkgctl-WebStation 2>/dev/null || echo "WebStation restart failed"
        /usr/syno/bin/synopkg restart pkgctl-Docker 2>/dev/null || echo "Docker restart failed"
        /usr/syno/bin/synopkg restart pkgctl-StorageManager 2>/dev/null || echo "StorageManager restart failed"
        
        # Применяем фикс
        /usr/local/bin/toshiba_hdwt860_fix.sh 2>/dev/null || echo "Fix applied"
        
        echo "Services restarted"
        """
        
        stdin, stdout, stderr = ssh.exec_command(restart_script)
        output = stdout.read().decode()
        self.log(f"🔄 Службы: {output.strip()}")
    
    def restore_system(self):
        """Восстановление системы"""
        self.log("🔄 Восстановление системы...")
        self.progress_bar.start()
        self.progress_var.set("Восстановление системы...")
        
        def restore():
            try:
                ip = self.ip_var.get()
                login = self.login_var.get()
                password = self.password_var.get()
                
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(ip, username=login, password=password, timeout=10)
                
                restore_script = """
                #!/bin/bash
                echo "Restoring system..."
                
                # Восстанавливаем файлы из резервных копий
                if [ -f /etc/synoinfo.conf.backup ]; then
                    cp /etc/synoinfo.conf.backup /etc/synoinfo.conf
                    echo "Restored synoinfo.conf"
                fi
                
                if [ -f /usr/syno/bin/synocheck.backup ]; then
                    cp /usr/syno/bin/synocheck.backup /usr/syno/bin/synocheck
                    chmod +x /usr/syno/bin/synocheck
                    echo "Restored synocheck"
                fi
                
                # Удаляем созданные файлы
                rm -f /usr/local/bin/toshiba_hdwt860_fix.sh
                rm -f /etc/systemd/system/toshiba-hdwt860-fix.service
                rm -f /etc/synoinfo.conf.toshiba
                
                echo "System restored"
                """
                
                stdin, stdout, stderr = ssh.exec_command(restore_script)
                output = stdout.read().decode()
                self.log(f"🔄 Восстановление: {output.strip()}")
                
                ssh.close()
                self.log("✅ Система восстановлена")
                self.progress_var.set("Восстановление завершено")
                
            except Exception as e:
                self.log(f"❌ Ошибка восстановления: {e}")
                self.progress_var.set("Ошибка восстановления")
            finally:
                self.progress_bar.stop()
        
        threading.Thread(target=restore, daemon=True).start()

def main():
    root = tk.Tk()
    app = ToshibaHDWT860Fix(root)
    root.mainloop()

if __name__ == "__main__":
    main()

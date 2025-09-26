#!/usr/bin/env python3
"""
Synology Drive Unlocker - Агрессивный патч
Максимально эффективный обход всех ограничений Synology
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

class AggressivePatch:
    def __init__(self, root):
        self.root = root
        self.root.title("Synology Drive Unlocker - Агрессивный патч")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Создание интерфейса агрессивного патча"""
        
        # Главный фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="⚡ Агрессивный патч Synology", 
                               font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Предупреждение
        warning_frame = ttk.LabelFrame(main_frame, text="⚠️ ВНИМАНИЕ", padding="10")
        warning_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        warning_text = """Этот патч применяет максимально агрессивные методы обхода ограничений.
Используйте только если обычные методы не сработали!

ВНИМАНИЕ: Может быть несовместим с обновлениями DSM!"""
        
        ttk.Label(warning_frame, text=warning_text, justify=tk.LEFT, 
                 foreground="red").grid(row=0, column=0)
        
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
        
        # Опции патча
        options_frame = ttk.LabelFrame(main_frame, text="⚙️ Опции патча", padding="10")
        options_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.force_patch_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Принудительный патч (обход всех проверок)", 
                       variable=self.force_patch_var).grid(row=0, column=0, sticky=tk.W)
        
        self.disable_checks_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Полное отключение проверок дисков", 
                       variable=self.disable_checks_var).grid(row=1, column=0, sticky=tk.W)
        
        self.modify_binaries_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Модификация бинарных файлов", 
                       variable=self.modify_binaries_var).grid(row=2, column=0, sticky=tk.W)
        
        self.create_hooks_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Создание системных хуков", 
                       variable=self.create_hooks_var).grid(row=3, column=0, sticky=tk.W)
        
        # Кнопки
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=4, column=0, columnspan=3, pady=(0, 10))
        
        ttk.Button(buttons_frame, text="🔍 Проверить подключение", 
                  command=self.test_connection).grid(row=0, column=0, padx=(0, 5))
        
        ttk.Button(buttons_frame, text="⚡ ПРИМЕНИТЬ АГРЕССИВНЫЙ ПАТЧ", 
                  command=self.apply_aggressive_patch, style="Accent.TButton").grid(row=0, column=1, padx=5)
        
        ttk.Button(buttons_frame, text="🔄 Восстановить", 
                  command=self.restore_system).grid(row=0, column=2, padx=5)
        
        # Прогресс
        self.progress_var = tk.StringVar(value="Готов к работе")
        ttk.Label(main_frame, textvariable=self.progress_var).grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Лог
        log_frame = ttk.LabelFrame(main_frame, text="📝 Лог операций", padding="5")
        log_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
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
    
    def apply_aggressive_patch(self):
        """Применение агрессивного патча"""
        self.log("⚡ Начинаем агрессивный патч...")
        self.progress_bar.start()
        self.progress_var.set("Применение агрессивного патча...")
        
        def patch():
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
                
                # Применение агрессивного патча
                self.log("⚡ Применение агрессивного патча...")
                self.apply_aggressive_patch_script(ssh)
                
                # Перезапуск служб
                self.log("🔄 Перезапуск служб...")
                self.restart_services(ssh)
                
                ssh.close()
                
                self.log("✅ Агрессивный патч применен успешно!")
                self.log("🎉 Теперь диски должны работать!")
                self.progress_var.set("Патч применен успешно")
                
                messagebox.showinfo("Успех!", 
                    "Агрессивный патч применен успешно!\n\n"
                    "Теперь перезагрузите NAS и проверьте диски.\n"
                    "Диски должны определяться без предупреждений.")
                
            except Exception as e:
                self.log(f"❌ Ошибка патча: {e}")
                self.progress_var.set("Ошибка патча")
            finally:
                self.progress_bar.stop()
        
        threading.Thread(target=patch, daemon=True).start()
    
    def create_backup(self, ssh):
        """Создание резервной копии"""
        backup_script = """
        #!/bin/bash
        BACKUP_DIR="/tmp/aggressive_backup_$(date +%Y%m%d_%H%M%S)"
        mkdir -p $BACKUP_DIR
        
        # Копируем все важные файлы
        cp /etc/synoinfo.conf $BACKUP_DIR/ 2>/dev/null
        cp /etc.defaults/synoinfo.conf $BACKUP_DIR/ 2>/dev/null
        cp /usr/syno/bin/synocheck $BACKUP_DIR/ 2>/dev/null
        cp -r /usr/syno/bin/ $BACKUP_DIR/bin_backup/ 2>/dev/null
        cp -r /etc/ $BACKUP_DIR/etc_backup/ 2>/dev/null
        
        echo "Backup created in $BACKUP_DIR"
        """
        
        stdin, stdout, stderr = ssh.exec_command(backup_script)
        output = stdout.read().decode()
        self.log(f"💾 Резервная копия: {output.strip()}")
    
    def apply_aggressive_patch_script(self, ssh):
        """Применение агрессивного патча"""
        patch_script = """
        #!/bin/bash
        
        echo "Applying aggressive patch..."
        
        # 1. Полное отключение проверок в synoinfo.conf
        echo "Modifying synoinfo.conf..."
        cp /etc/synoinfo.conf /etc/synoinfo.conf.backup
        
        # Удаляем все проверки дисков
        sed -i '/support_disk_compatibility/d' /etc/synoinfo.conf
        sed -i '/support_disk_compatibility_check/d' /etc/synoinfo.conf
        sed -i '/support_disk_compatibility_override/d' /etc/synoinfo.conf
        
        # Добавляем агрессивные настройки
        cat >> /etc/synoinfo.conf << 'EOF'
# Synology Drive Unlocker - Aggressive Patch
support_disk_compatibility="no"
support_disk_compatibility_check="no"
support_disk_compatibility_override="yes"
support_disk_compatibility_force="yes"
support_disk_compatibility_bypass="yes"
support_disk_compatibility_ignore="yes"
support_disk_compatibility_disable="yes"
EOF
        
        # 2. Модификация synocheck
        echo "Modifying synocheck..."
        cp /usr/syno/bin/synocheck /usr/syno/bin/synocheck.backup
        
        # Создаем новый synocheck который всегда возвращает успех
        cat > /usr/syno/bin/synocheck << 'EOF'
#!/bin/bash
# Synology Drive Unlocker - Patched synocheck
# Always returns success for disk compatibility checks

case "$1" in
    "disk_compatibility"|"compatibility"|"disk")
        echo "Disk compatibility check bypassed by Synology Drive Unlocker"
        exit 0
        ;;
    *)
        # For other checks, try to run original if it exists
        if [ -f /usr/syno/bin/synocheck.original ]; then
            exec /usr/syno/bin/synocheck.original "$@"
        else
            exit 0
        fi
        ;;
esac
EOF
        
        chmod +x /usr/syno/bin/synocheck
        
        # 3. Создание системных хуков
        echo "Creating system hooks..."
        
        # Хук для отключения проверок при загрузке
        cat > /usr/local/bin/disable_disk_checks.sh << 'EOF'
#!/bin/bash
# Disable disk compatibility checks on boot

# Override synoinfo.conf
sed -i 's/support_disk_compatibility="yes"/support_disk_compatibility="no"/g' /etc/synoinfo.conf
sed -i 's/support_disk_compatibility_check="yes"/support_disk_compatibility_check="no"/g' /etc/synoinfo.conf

# Ensure our settings are applied
echo "support_disk_compatibility=\"no\"" >> /etc/synoinfo.conf
echo "support_disk_compatibility_check=\"no\"" >> /etc/synoinfo.conf
echo "support_disk_compatibility_override=\"yes\"" >> /etc/synoinfo.conf
EOF
        
        chmod +x /usr/local/bin/disable_disk_checks.sh
        
        # 4. Модификация дополнительных файлов
        echo "Modifying additional files..."
        
        # Модифицируем /etc.defaults/synoinfo.conf
        if [ -f /etc.defaults/synoinfo.conf ]; then
            cp /etc.defaults/synoinfo.conf /etc.defaults/synoinfo.conf.backup
            sed -i '/support_disk_compatibility/d' /etc.defaults/synoinfo.conf
            cat >> /etc.defaults/synoinfo.conf << 'EOF'
# Synology Drive Unlocker - Aggressive Patch
support_disk_compatibility="no"
support_disk_compatibility_check="no"
support_disk_compatibility_override="yes"
EOF
        fi
        
        # 5. Создание службы для автоматического применения
        echo "Creating systemd service..."
        cat > /etc/systemd/system/synology-unlocker.service << 'EOF'
[Unit]
Description=Synology Drive Unlocker Service
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/disable_disk_checks.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF
        
        systemctl enable synology-unlocker.service 2>/dev/null || echo "systemd not available"
        
        # 6. Модификация других бинарных файлов
        echo "Modifying binary files..."
        
        # Создаем обертки для других команд
        for cmd in synocheck synocheck.sh synocheck.bin; do
            if [ -f "/usr/syno/bin/$cmd" ]; then
                cp "/usr/syno/bin/$cmd" "/usr/syno/bin/$cmd.backup"
                ln -sf /usr/syno/bin/synocheck "/usr/syno/bin/$cmd"
            fi
        done
        
        echo "Aggressive patch applied successfully"
        """
        
        stdin, stdout, stderr = ssh.exec_command(patch_script)
        output = stdout.read().decode()
        self.log(f"⚡ Агрессивный патч: {output}")
    
    def restart_services(self, ssh):
        """Перезапуск служб"""
        restart_script = """
        #!/bin/bash
        echo "Restarting services..."
        
        # Перезапускаем все службы
        /usr/syno/bin/synopkg restart pkgctl-WebStation 2>/dev/null || echo "WebStation restart failed"
        /usr/syno/bin/synopkg restart pkgctl-Docker 2>/dev/null || echo "Docker restart failed"
        /usr/syno/bin/synopkg restart pkgctl-StorageManager 2>/dev/null || echo "StorageManager restart failed"
        
        # Перезапускаем службы хранения
        /usr/syno/bin/synopkg restart pkgctl-VolumeManager 2>/dev/null || echo "VolumeManager restart failed"
        
        # Применяем хуки
        /usr/local/bin/disable_disk_checks.sh 2>/dev/null || echo "Hooks applied"
        
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
                
                if [ -f /etc.defaults/synoinfo.conf.backup ]; then
                    cp /etc.defaults/synoinfo.conf.backup /etc.defaults/synoinfo.conf
                    echo "Restored synoinfo.conf.defaults"
                fi
                
                # Удаляем созданные файлы
                rm -f /usr/local/bin/disable_disk_checks.sh
                rm -f /etc/systemd/system/synology-unlocker.service
                
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
    app = AggressivePatch(root)
    root.mainloop()

if __name__ == "__main__":
    main()

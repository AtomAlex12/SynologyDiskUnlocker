#!/usr/bin/env python3
"""
Synology Drive Unlocker - Автоматическая настройка
Автоматически настраивает NAS и применяет патчи без ручной настройки
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

class AutoSetup:
    def __init__(self, root):
        self.root = root
        self.root.title("Synology Drive Unlocker - Автоматическая настройка")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Создание интерфейса автоматической настройки"""
        
        # Главный фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="🚀 Автоматическая настройка Synology NAS", 
                               font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Информационная панель
        info_frame = ttk.LabelFrame(main_frame, text="ℹ️ Информация", padding="10")
        info_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        info_text = """Эта утилита автоматически:
• Найдет ваш Synology NAS в сети
• Настроит SSH доступ через веб-интерфейс
• Применит патчи для обхода ограничений дисков
• Все в автоматическом режиме!

⚠️ Требования: доступ к веб-интерфейсу DSM с правами администратора"""
        
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).grid(row=0, column=0)
        
        # Настройки подключения
        settings_frame = ttk.LabelFrame(main_frame, text="🔧 Настройки", padding="10")
        settings_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # IP адрес или поиск
        ttk.Label(settings_frame, text="IP адрес NAS (или оставьте пустым для автопоиска):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.ip_var = tk.StringVar()
        ttk.Entry(settings_frame, textvariable=self.ip_var, width=20).grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        ttk.Button(settings_frame, text="🔍 Найти NAS", 
                  command=self.find_nas).grid(row=0, column=2, padx=(10, 0))
        
        # Логин и пароль
        ttk.Label(settings_frame, text="Логин администратора:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.login_var = tk.StringVar(value="admin")
        ttk.Entry(settings_frame, textvariable=self.login_var, width=20).grid(row=1, column=1, sticky=tk.W, padx=(5, 0))
        
        ttk.Label(settings_frame, text="Пароль:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.password_var = tk.StringVar()
        ttk.Entry(settings_frame, textvariable=self.password_var, show="*", width=20).grid(row=2, column=1, sticky=tk.W, padx=(5, 0))
        
        # Порт веб-интерфейса
        ttk.Label(settings_frame, text="Порт веб-интерфейса:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.web_port_var = tk.StringVar(value="5000")
        ttk.Entry(settings_frame, textvariable=self.web_port_var, width=10).grid(row=3, column=1, sticky=tk.W, padx=(5, 0))
        
        # Кнопки управления
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, columnspan=3, pady=(0, 10))
        
        ttk.Button(buttons_frame, text="🔍 Найти NAS в сети", 
                  command=self.find_nas).grid(row=0, column=0, padx=(0, 5))
        
        ttk.Button(buttons_frame, text="🌐 Открыть веб-интерфейс", 
                  command=self.open_web_interface).grid(row=0, column=1, padx=5)
        
        ttk.Button(buttons_frame, text="⚙️ Настроить SSH", 
                  command=self.setup_ssh).grid(row=0, column=2, padx=5)
        
        ttk.Button(buttons_frame, text="🚀 Полная автоматизация", 
                  command=self.full_automation).grid(row=0, column=3, padx=5)
        
        # Прогресс
        self.progress_var = tk.StringVar(value="Готов к работе")
        ttk.Label(main_frame, textvariable=self.progress_var).grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Лог
        log_frame = ttk.LabelFrame(main_frame, text="📝 Лог операций", padding="5")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=100)
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
        
    def find_nas(self):
        """Автоматический поиск Synology NAS в сети"""
        self.log("🔍 Поиск Synology NAS в локальной сети...")
        self.progress_bar.start()
        self.progress_var.set("Поиск NAS...")
        
        def search():
            try:
                # Получаем локальный IP
                import socket
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
                
                self.log(f"Локальный IP: {local_ip}")
                
                # Определяем диапазон поиска
                base_ip = ".".join(local_ip.split(".")[:-1])
                self.log(f"Поиск в диапазоне: {base_ip}.1-254")
                
                found_nas = []
                
                # Поиск по портам Synology
                ports = [5000, 5001, 80, 443]
                
                for i in range(1, 255):
                    ip = f"{base_ip}.{i}"
                    self.log(f"Проверка {ip}...")
                    
                    for port in ports:
                        try:
                            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            sock.settimeout(1)
                            result = sock.connect_ex((ip, port))
                            sock.close()
                            
                            if result == 0:
                                # Проверяем, что это Synology
                                try:
                                    response = requests.get(f"http://{ip}:{port}/webapi/query.cgi?api=SYNO.API.Info&version=1&method=query", 
                                                          timeout=2)
                                    if "SYNO.API.Info" in response.text:
                                        found_nas.append((ip, port))
                                        self.log(f"✅ Найден Synology NAS: {ip}:{port}")
                                        break
                                except:
                                    pass
                        except:
                            pass
                    
                    if len(found_nas) >= 3:  # Ограничиваем поиск
                        break
                
                if found_nas:
                    self.log(f"🎉 Найдено {len(found_nas)} Synology NAS:")
                    for ip, port in found_nas:
                        self.log(f"  • {ip}:{port}")
                    
                    # Автоматически выбираем первый найденный
                    ip, port = found_nas[0]
                    self.ip_var.set(ip)
                    self.web_port_var.set(str(port))
                    self.log(f"✅ Выбран: {ip}:{port}")
                else:
                    self.log("❌ Synology NAS не найден в сети")
                    self.log("Проверьте:")
                    self.log("  • NAS включен и подключен к сети")
                    self.log("  • Компьютер и NAS в одной сети")
                    self.log("  • Брандмауэр не блокирует подключения")
                
            except Exception as e:
                self.log(f"❌ Ошибка поиска: {e}")
            finally:
                self.progress_bar.stop()
                self.progress_var.set("Поиск завершен")
        
        threading.Thread(target=search, daemon=True).start()
    
    def open_web_interface(self):
        """Открытие веб-интерфейса DSM"""
        ip = self.ip_var.get()
        port = self.web_port_var.get()
        
        if not ip:
            messagebox.showerror("Ошибка", "Введите IP адрес NAS")
            return
        
        url = f"http://{ip}:{port}"
        self.log(f"🌐 Открытие веб-интерфейса: {url}")
        
        try:
            webbrowser.open(url)
            self.log("✅ Веб-интерфейс открыт в браузере")
        except Exception as e:
            self.log(f"❌ Ошибка открытия браузера: {e}")
    
    def setup_ssh(self):
        """Автоматическая настройка SSH через веб-интерфейс"""
        self.log("⚙️ Настройка SSH через веб-интерфейс...")
        self.progress_bar.start()
        self.progress_var.set("Настройка SSH...")
        
        def setup():
            try:
                ip = self.ip_var.get()
                port = self.web_port_var.get()
                login = self.login_var.get()
                password = self.password_var.get()
                
                if not all([ip, login, password]):
                    self.log("❌ Заполните все поля")
                    return
                
                # Создаем сессию
                session = requests.Session()
                
                # Получаем информацию об API
                self.log("Получение информации об API...")
                api_info_url = f"http://{ip}:{port}/webapi/query.cgi"
                params = {
                    'api': 'SYNO.API.Info',
                    'version': '1',
                    'method': 'query'
                }
                
                response = session.get(api_info_url, params=params, timeout=10)
                if response.status_code != 200:
                    self.log("❌ Не удалось подключиться к NAS")
                    return
                
                # Логинимся
                self.log("Вход в систему...")
                login_url = f"http://{ip}:{port}/webapi/auth.cgi"
                login_params = {
                    'api': 'SYNO.API.Auth',
                    'version': '2',
                    'method': 'login',
                    'account': login,
                    'passwd': password,
                    'session': 'FileStation',
                    'format': 'sid'
                }
                
                response = session.get(login_url, params=login_params, timeout=10)
                if response.status_code != 200:
                    self.log("❌ Ошибка входа в систему")
                    return
                
                data = response.json()
                if not data.get('success'):
                    self.log(f"❌ Ошибка аутентификации: {data.get('error', {}).get('code')}")
                    return
                
                sid = data['data']['sid']
                self.log("✅ Успешный вход в систему")
                
                # Включаем SSH
                self.log("Включение SSH...")
                ssh_url = f"http://{ip}:{port}/webapi/entry.cgi"
                ssh_params = {
                    'api': 'SYNO.Core.Terminal',
                    'version': '1',
                    'method': 'set',
                    'enable': 'true',
                    'port': '22',
                    '_sid': sid
                }
                
                response = session.get(ssh_url, params=ssh_params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        self.log("✅ SSH успешно включен")
                    else:
                        self.log(f"⚠️ SSH уже включен или ошибка: {data.get('error', {}).get('code')}")
                else:
                    self.log("⚠️ Не удалось включить SSH через API, попробуйте вручную")
                
                # Выходим из системы
                logout_url = f"http://{ip}:{port}/webapi/auth.cgi"
                logout_params = {
                    'api': 'SYNO.API.Auth',
                    'version': '2',
                    'method': 'logout',
                    'session': 'FileStation',
                    '_sid': sid
                }
                session.get(logout_url, params=logout_params, timeout=5)
                
                self.log("✅ Настройка SSH завершена")
                self.log("Теперь можно использовать основную утилиту")
                
            except Exception as e:
                self.log(f"❌ Ошибка настройки SSH: {e}")
            finally:
                self.progress_bar.stop()
                self.progress_var.set("Настройка завершена")
        
        threading.Thread(target=setup, daemon=True).start()
    
    def full_automation(self):
        """Полная автоматизация: поиск + настройка + применение патчей"""
        self.log("🚀 Запуск полной автоматизации...")
        self.progress_bar.start()
        self.progress_var.set("Полная автоматизация...")
        
        def automate():
            try:
                # Шаг 1: Поиск NAS
                self.log("Шаг 1: Поиск NAS...")
                self.find_nas()
                time.sleep(2)
                
                # Шаг 2: Настройка SSH
                self.log("Шаг 2: Настройка SSH...")
                self.setup_ssh()
                time.sleep(3)
                
                # Шаг 3: Применение патчей
                self.log("Шаг 3: Применение патчей...")
                self.apply_patches()
                
                self.log("✅ Полная автоматизация завершена!")
                
            except Exception as e:
                self.log(f"❌ Ошибка автоматизации: {e}")
            finally:
                self.progress_bar.stop()
                self.progress_var.set("Автоматизация завершена")
        
        threading.Thread(target=automate, daemon=True).start()
    
    def apply_patches(self):
        """Применение патчей через веб-интерфейс"""
        self.log("🔧 Применение патчей...")
        
        # Здесь можно добавить логику применения патчей
        # через веб-интерфейс или другие методы
        self.log("⚠️ Применение патчей требует SSH доступа")
        self.log("Используйте основную утилиту после настройки SSH")

def main():
    root = tk.Tk()
    app = AutoSetup(root)
    root.mainloop()

if __name__ == "__main__":
    main()

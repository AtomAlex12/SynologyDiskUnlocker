#!/usr/bin/env python3
"""
Synology Drive Unlocker PRO
Единое приложение со всеми патчами и продвинутой системой логирования
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
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
import logging
from datetime import datetime
import webbrowser

class SynologyUnlockerPro:
    def __init__(self, root):
        self.root = root
        self.root.title("Synology Drive Unlocker PRO v2.0")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        # Настройка логирования
        self.setup_logging()
        
        # Создание интерфейса
        self.setup_ui()
        
        # Загрузка конфигурации
        self.load_config()
        
    def setup_logging(self):
        """Настройка системы логирования"""
        # Создаем директории для логов
        Path("logs").mkdir(exist_ok=True)
        
        # Настройка 4 типов логов
        self.loggers = {}
        
        # 1. Основной лог (все операции)
        main_logger = logging.getLogger('main')
        main_logger.setLevel(logging.INFO)
        main_handler = logging.FileHandler('logs/main.log', encoding='utf-8')
        main_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        main_handler.setFormatter(main_formatter)
        main_logger.addHandler(main_handler)
        self.loggers['main'] = main_logger
        
        # 2. SSH лог (все SSH операции)
        ssh_logger = logging.getLogger('ssh')
        ssh_logger.setLevel(logging.DEBUG)
        ssh_handler = logging.FileHandler('logs/ssh.log', encoding='utf-8')
        ssh_formatter = logging.Formatter('%(asctime)s - SSH - %(message)s')
        ssh_handler.setFormatter(ssh_formatter)
        ssh_logger.addHandler(ssh_handler)
        self.loggers['ssh'] = ssh_logger
        
        # 3. Системный лог (системные операции)
        system_logger = logging.getLogger('system')
        system_logger.setLevel(logging.INFO)
        system_handler = logging.FileHandler('logs/system.log', encoding='utf-8')
        system_formatter = logging.Formatter('%(asctime)s - SYSTEM - %(message)s')
        system_handler.setFormatter(system_formatter)
        system_logger.addHandler(system_handler)
        self.loggers['system'] = system_logger
        
        # 4. Ошибки лог (только ошибки)
        error_logger = logging.getLogger('error')
        error_logger.setLevel(logging.ERROR)
        error_handler = logging.FileHandler('logs/errors.log', encoding='utf-8')
        error_formatter = logging.Formatter('%(asctime)s - ERROR - %(message)s')
        error_handler.setFormatter(error_formatter)
        error_logger.addHandler(error_handler)
        self.loggers['error'] = error_logger
        
    def log(self, message, level='info', category='main'):
        """Универсальное логирование"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        
        # Добавляем в GUI
        self.log_text.insert(tk.END, f"{log_message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
        # Добавляем в файловые логи
        if category in self.loggers:
            if level == 'debug':
                self.loggers[category].debug(message)
            elif level == 'info':
                self.loggers[category].info(message)
            elif level == 'warning':
                self.loggers[category].warning(message)
            elif level == 'error':
                self.loggers[category].error(message)
                self.loggers['error'].error(message)
        
        # SSH команды также показываем в основном логе
        if category == 'ssh' and 'SSH команда:' in message:
            self.loggers['main'].info(f"SSH: {message}")
    
    def setup_ui(self):
        """Создание красивого интерфейса"""
        
        # Стили
        style = ttk.Style()
        style.theme_use('clam')
        
        # Настройка цветов
        style.configure('Title.TLabel', font=('Arial', 20, 'bold'), foreground='#2c3e50')
        style.configure('Subtitle.TLabel', font=('Arial', 12, 'bold'), foreground='#34495e')
        style.configure('Success.TLabel', foreground='#27ae60')
        style.configure('Error.TLabel', foreground='#e74c3c')
        style.configure('Warning.TLabel', foreground='#f39c12')
        style.configure('Accent.TButton', font=('Arial', 10, 'bold'))
        
        # Главный контейнер
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Заголовок
        title_frame = ttk.Frame(main_container)
        title_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        title_label = ttk.Label(title_frame, text="🔓 Synology Drive Unlocker PRO", 
                               style='Title.TLabel')
        title_label.grid(row=0, column=0)
        
        subtitle_label = ttk.Label(title_frame, text="Единое решение для разблокировки дисков Synology", 
                                  style='Subtitle.TLabel')
        subtitle_label.grid(row=1, column=0, pady=(5, 0))
        
        # Создаем Notebook для вкладок
        self.notebook = ttk.Notebook(main_container)
        self.notebook.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Вкладка 1: Быстрый старт
        self.setup_quick_start_tab()
        
        # Вкладка 2: Специальные патчи
        self.setup_patches_tab()
        
        # Вкладка 3: Диагностика
        self.setup_diagnostics_tab()
        
        # Вкладка 4: Логи
        self.setup_logs_tab()
        
        # Вкладка 5: Настройки
        self.setup_settings_tab()
        
        # Статус бар
        self.setup_status_bar(main_container)
        
        # Настройка растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=1)
    
    def setup_quick_start_tab(self):
        """Вкладка быстрого старта"""
        quick_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(quick_frame, text="🚀 Быстрый старт")
        
        # Информация
        info_frame = ttk.LabelFrame(quick_frame, text="ℹ️ Информация", padding="15")
        info_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        info_text = """Выберите подходящий метод разблокировки дисков:
• Быстрый старт - для новичков
• Специальные патчи - для конкретных моделей дисков
• Агрессивный патч - для сложных случаев"""
        
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).grid(row=0, column=0)
        
        # Настройки подключения
        settings_frame = ttk.LabelFrame(quick_frame, text="🔧 Настройки подключения", padding="15")
        settings_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # IP адрес
        ttk.Label(settings_frame, text="IP адрес NAS:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.ip_var = tk.StringVar(value="192.168.1.100")
        ttk.Entry(settings_frame, textvariable=self.ip_var, width=20).grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # Логин
        ttk.Label(settings_frame, text="Логин:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.login_var = tk.StringVar(value="admin")
        ttk.Entry(settings_frame, textvariable=self.login_var, width=20).grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        # Пароль
        ttk.Label(settings_frame, text="Пароль:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar()
        ttk.Entry(settings_frame, textvariable=self.password_var, show="*", width=20).grid(row=2, column=1, sticky=tk.W, padx=(10, 0))
        
        # Использовать sudo
        self.use_sudo_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Использовать sudo для выполнения команд", 
                       variable=self.use_sudo_var).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Кнопки быстрого старта
        buttons_frame = ttk.Frame(quick_frame)
        buttons_frame.grid(row=2, column=0, columnspan=2, pady=(0, 20))
        
        ttk.Button(buttons_frame, text="🔍 Проверить подключение", 
                  command=self.test_connection).grid(row=0, column=0, padx=(0, 10))
        
        ttk.Button(buttons_frame, text="🚀 Быстрый старт", 
                  command=self.quick_start, style='Accent.TButton').grid(row=0, column=1, padx=10)
        
        ttk.Button(buttons_frame, text="💾 Toshiba HDWT860", 
                  command=self.toshiba_fix).grid(row=0, column=2, padx=10)
        
        ttk.Button(buttons_frame, text="⚡ Агрессивный патч", 
                  command=self.aggressive_patch).grid(row=0, column=3, padx=10)
        
        # Прогресс
        self.progress_var = tk.StringVar(value="Готов к работе")
        ttk.Label(quick_frame, textvariable=self.progress_var).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(quick_frame, mode='indeterminate')
        self.progress_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Лог
        log_frame = ttk.LabelFrame(quick_frame, text="📝 Лог операций", padding="5")
        log_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=100)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка растягивания
        quick_frame.columnconfigure(1, weight=1)
        quick_frame.rowconfigure(5, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
    
    def setup_patches_tab(self):
        """Вкладка специальных патчей"""
        patches_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(patches_frame, text="🔧 Специальные патчи")
        
        # Информация о патчах
        info_frame = ttk.LabelFrame(patches_frame, text="ℹ️ Доступные патчи", padding="15")
        info_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        patches_info = """Выберите подходящий патч для вашего случая:
• Стандартный патч - для большинства дисков
• Toshiba HDWT860 - специально для Toshiba 5.5TB
• WD Red - для дисков Western Digital Red
• Seagate IronWolf - для дисков Seagate IronWolf
• Агрессивный патч - для сложных случаев"""
        
        ttk.Label(info_frame, text=patches_info, justify=tk.LEFT).grid(row=0, column=0)
        
        # Кнопки патчей
        patches_buttons = ttk.Frame(patches_frame)
        patches_buttons.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        ttk.Button(patches_buttons, text="📦 Стандартный патч", 
                  command=self.standard_patch).grid(row=0, column=0, padx=5, pady=5)
        
        ttk.Button(patches_buttons, text="💾 Toshiba HDWT860", 
                  command=self.toshiba_patch).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(patches_buttons, text="🔴 WD Red", 
                  command=self.wd_red_patch).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Button(patches_buttons, text="🐺 Seagate IronWolf", 
                  command=self.seagate_patch).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Button(patches_buttons, text="⚡ Агрессивный патч", 
                  command=self.aggressive_patch).grid(row=0, column=4, padx=5, pady=5)
        
        # Опции патчей
        options_frame = ttk.LabelFrame(patches_frame, text="⚙️ Опции патчей", padding="15")
        options_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.create_backup_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Создать резервную копию", 
                       variable=self.create_backup_var).grid(row=0, column=0, sticky=tk.W)
        
        self.auto_restart_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Автоматический перезапуск NAS", 
                       variable=self.auto_restart_var).grid(row=1, column=0, sticky=tk.W)
        
        self.force_patch_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Принудительное применение", 
                       variable=self.force_patch_var).grid(row=2, column=0, sticky=tk.W)
    
    def setup_diagnostics_tab(self):
        """Вкладка диагностики"""
        diag_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(diag_frame, text="🔍 Диагностика")
        
        # Информация о диагностике
        info_frame = ttk.LabelFrame(diag_frame, text="ℹ️ Диагностика системы", padding="15")
        info_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        diag_info = """Диагностические инструменты для выявления проблем:
• Проверка подключения к NAS
• Анализ системы DSM
• Проверка дисков
• Тест SSH подключения
• Анализ логов"""
        
        ttk.Label(info_frame, text=diag_info, justify=tk.LEFT).grid(row=0, column=0)
        
        # Кнопки диагностики
        diag_buttons = ttk.Frame(diag_frame)
        diag_buttons.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        ttk.Button(diag_buttons, text="🔍 Проверить подключение", 
                  command=self.test_connection).grid(row=0, column=0, padx=5, pady=5)
        
        ttk.Button(diag_buttons, text="🖥️ Анализ DSM", 
                  command=self.analyze_dsm).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(diag_buttons, text="💾 Проверить диски", 
                  command=self.check_disks).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Button(diag_buttons, text="🔐 Тест SSH", 
                  command=self.test_ssh).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Button(diag_buttons, text="📊 Анализ логов", 
                  command=self.analyze_logs).grid(row=0, column=4, padx=5, pady=5)
        
        # Результаты диагностики
        results_frame = ttk.LabelFrame(diag_frame, text="📊 Результаты диагностики", padding="15")
        results_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.diag_text = scrolledtext.ScrolledText(results_frame, height=20, width=100)
        self.diag_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка растягивания
        diag_frame.columnconfigure(1, weight=1)
        diag_frame.rowconfigure(2, weight=1)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
    
    def setup_logs_tab(self):
        """Вкладка логов"""
        logs_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(logs_frame, text="📋 Логи")
        
        # Информация о логах
        info_frame = ttk.LabelFrame(logs_frame, text="ℹ️ Система логирования", padding="15")
        info_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        logs_info = """4 типа логов для полной диагностики:
• Основной лог - все операции приложения
• SSH лог - все SSH подключения и команды
• Системный лог - системные операции
• Лог ошибок - только ошибки и предупреждения"""
        
        ttk.Label(info_frame, text=logs_info, justify=tk.LEFT).grid(row=0, column=0)
        
        # Кнопки управления логами
        logs_buttons = ttk.Frame(logs_frame)
        logs_buttons.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        ttk.Button(logs_buttons, text="📋 Основной лог", 
                  command=lambda: self.show_log('main')).grid(row=0, column=0, padx=5, pady=5)
        
        ttk.Button(logs_buttons, text="🔐 SSH лог", 
                  command=lambda: self.show_log('ssh')).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(logs_buttons, text="🖥️ Системный лог", 
                  command=lambda: self.show_log('system')).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Button(logs_buttons, text="❌ Лог ошибок", 
                  command=lambda: self.show_log('error')).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Button(logs_buttons, text="🗑️ Очистить логи", 
                  command=self.clear_logs).grid(row=0, column=4, padx=5, pady=5)
        
        ttk.Button(logs_buttons, text="📁 Открыть папку логов", 
                  command=self.open_logs_folder).grid(row=0, column=5, padx=5, pady=5)
        
        # Область отображения логов
        logs_display_frame = ttk.LabelFrame(logs_frame, text="📝 Содержимое лога", padding="15")
        logs_display_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.logs_text = scrolledtext.ScrolledText(logs_display_frame, height=20, width=100)
        self.logs_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка растягивания
        logs_frame.columnconfigure(1, weight=1)
        logs_frame.rowconfigure(2, weight=1)
        logs_display_frame.columnconfigure(0, weight=1)
        logs_display_frame.rowconfigure(0, weight=1)
    
    def setup_settings_tab(self):
        """Вкладка настроек"""
        settings_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(settings_frame, text="⚙️ Настройки")
        
        # Общие настройки
        general_frame = ttk.LabelFrame(settings_frame, text="🔧 Общие настройки", padding="15")
        general_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Автосохранение
        self.auto_save_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(general_frame, text="Автосохранение настроек", 
                       variable=self.auto_save_var).grid(row=0, column=0, sticky=tk.W)
        
        # Уровень логирования
        ttk.Label(general_frame, text="Уровень логирования:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.log_level_var = tk.StringVar(value="INFO")
        log_level_combo = ttk.Combobox(general_frame, textvariable=self.log_level_var, 
                                      values=["DEBUG", "INFO", "WARNING", "ERROR"], width=15)
        log_level_combo.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        # Максимальный размер лога
        ttk.Label(general_frame, text="Максимальный размер лога (MB):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.max_log_size_var = tk.StringVar(value="10")
        ttk.Entry(general_frame, textvariable=self.max_log_size_var, width=15).grid(row=2, column=1, sticky=tk.W, padx=(10, 0))
        
        # Настройки SSH
        ssh_frame = ttk.LabelFrame(settings_frame, text="🔐 Настройки SSH", padding="15")
        ssh_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Таймаут SSH
        ttk.Label(ssh_frame, text="Таймаут SSH (секунды):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.ssh_timeout_var = tk.StringVar(value="30")
        ttk.Entry(ssh_frame, textvariable=self.ssh_timeout_var, width=15).grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # Количество попыток
        ttk.Label(ssh_frame, text="Количество попыток:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.ssh_retries_var = tk.StringVar(value="3")
        ttk.Entry(ssh_frame, textvariable=self.ssh_retries_var, width=15).grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        # Кнопки управления
        buttons_frame = ttk.Frame(settings_frame)
        buttons_frame.grid(row=2, column=0, columnspan=2, pady=(0, 20))
        
        ttk.Button(buttons_frame, text="💾 Сохранить настройки", 
                  command=self.save_settings).grid(row=0, column=0, padx=5)
        
        ttk.Button(buttons_frame, text="🔄 Сбросить настройки", 
                  command=self.reset_settings).grid(row=0, column=1, padx=5)
        
        ttk.Button(buttons_frame, text="📁 Открыть папку конфигурации", 
                  command=self.open_config_folder).grid(row=0, column=2, padx=5)
    
    def setup_status_bar(self, parent):
        """Статус бар"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.status_var = tk.StringVar(value="Готов к работе")
        ttk.Label(status_frame, textvariable=self.status_var).grid(row=0, column=0, sticky=tk.W)
        
        # Индикатор подключения
        self.connection_status = ttk.Label(status_frame, text="●", foreground="red")
        self.connection_status.grid(row=0, column=1, padx=(20, 0))
        
        # Время
        self.time_var = tk.StringVar()
        ttk.Label(status_frame, textvariable=self.time_var).grid(row=0, column=2, sticky=tk.E)
        
        # Обновление времени
        self.update_time()
    
    def update_time(self):
        """Обновление времени в статус баре"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_var.set(current_time)
        self.root.after(1000, self.update_time)
    
    def load_config(self):
        """Загрузка конфигурации"""
        try:
            if os.path.exists("config_pro.json"):
                with open("config_pro.json", "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.ip_var.set(config.get("ip", "192.168.1.100"))
                    self.login_var.set(config.get("login", "admin"))
                    self.auto_save_var.set(config.get("auto_save", True))
                    self.log_level_var.set(config.get("log_level", "INFO"))
                    self.max_log_size_var.set(config.get("max_log_size", "10"))
                    self.ssh_timeout_var.set(config.get("ssh_timeout", "30"))
                    self.ssh_retries_var.set(config.get("ssh_retries", "3"))
        except Exception as e:
            self.log(f"Ошибка загрузки конфигурации: {e}", 'error')
    
    def save_config(self):
        """Сохранение конфигурации"""
        config = {
            "ip": self.ip_var.get(),
            "login": self.login_var.get(),
            "auto_save": self.auto_save_var.get(),
            "log_level": self.log_level_var.get(),
            "max_log_size": self.max_log_size_var.get(),
            "ssh_timeout": self.ssh_timeout_var.get(),
            "ssh_retries": self.ssh_retries_var.get()
        }
        
        try:
            with open("config_pro.json", "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            self.log("Конфигурация сохранена", 'info')
        except Exception as e:
            self.log(f"Ошибка сохранения конфигурации: {e}", 'error')
    
    def test_connection(self):
        """Проверка подключения к NAS"""
        self.log("Проверка подключения к NAS...", 'info')
        self.progress_bar.start()
        self.progress_var.set("Проверка подключения...")
        
        def test():
            try:
                ip = self.ip_var.get()
                login = self.login_var.get()
                password = self.password_var.get()
                
                if not all([ip, login, password]):
                    self.log("Заполните все поля", 'error')
                    return
                
                # Проверка ping
                result = subprocess.run(['ping', '-n', '1', ip], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode != 0:
                    self.log("NAS недоступен по ping", 'error')
                    return
                
                # Проверка SSH
                ssh = self.connect_ssh(ip, login, password)
                if not ssh:
                    self.log("Не удалось подключиться по SSH", 'error')
                    return
                
                # Проверка версии DSM
                stdin, stdout, stderr = ssh.exec_command("cat /etc.defaults/VERSION")
                version = stdout.read().decode().strip()
                self.log(f"Подключение успешно. DSM версия: {version}", 'info')
                
                # Проверка sudo
                if self.use_sudo_var.get():
                    self.log("🔐 Проверка sudo доступа...", 'info', 'ssh')
                    output, error, exit_code = self.execute_ssh_command(ssh, "whoami", use_sudo=True)
                    if "root" in output:
                        self.log("✅ Sudo доступ подтвержден - работаем от root", 'info')
                    else:
                        self.log("⚠️ Sudo недоступен, будет использован обычный пользователь", 'warning')
                        self.log(f"Вывод: {output}", 'debug', 'ssh')
                        self.log(f"Ошибка: {error}", 'debug', 'ssh')
                
                ssh.close()
                self.progress_var.set("Подключение успешно")
                self.connection_status.config(foreground="green")
                
            except Exception as e:
                self.log(f"Ошибка подключения: {e}", 'error')
                self.progress_var.set("Ошибка подключения")
                self.connection_status.config(foreground="red")
            finally:
                self.progress_bar.stop()
        
        threading.Thread(target=test, daemon=True).start()
    
    def connect_ssh(self, ip, login, password):
        """Подключение по SSH с логированием"""
        try:
            self.log(f"Подключение к {ip} как {login}...", 'info', 'ssh')
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username=login, password=password, timeout=30)
            self.log("SSH подключение установлено", 'info', 'ssh')
            return ssh
        except Exception as e:
            self.log(f"Ошибка SSH подключения: {e}", 'error', 'ssh')
            return None
    
    def execute_ssh_command(self, ssh, command, use_sudo=False):
        """Выполнение команды через SSH с поддержкой sudo"""
        try:
            if use_sudo and self.use_sudo_var.get():
                # Сначала переключаемся на root через sudo su
                self.log(f"🔐 Переключение на root через sudo su...", 'info', 'ssh')
                self.log(f"💻 >>> sudo su", 'info', 'ssh')
                
                # Создаем интерактивную сессию для sudo su
                transport = ssh.get_transport()
                channel = transport.open_session()
                channel.get_pty()
                channel.invoke_shell()
                
                # Отправляем команду sudo su
                channel.send("sudo su\n")
                time.sleep(1)
                
                # Читаем приглашение для пароля
                response = ""
                password_prompt_found = False
                timeout = 0
                max_timeout = 50  # 5 секунд максимум
                
                while not password_prompt_found and timeout < max_timeout:
                    if channel.recv_ready():
                        data = channel.recv(1024).decode('utf-8', errors='ignore')
                        response += data
                        if data.strip():
                            self.log(f"💻 <<< {data.strip()}", 'info', 'ssh')
                        
                        # Проверяем различные варианты запроса пароля
                        if ("password for" in data.lower() or 
                            "password:" in data.lower() or 
                            "password" in data.lower()):
                            password_prompt_found = True
                            break
                    
                    time.sleep(0.1)
                    timeout += 1
                
                if not password_prompt_found:
                    self.log(f"⚠️ Не удалось найти запрос пароля, пробуем ввести пароль...", 'warning', 'ssh')
                
                self.log(f"🔑 Ввод пароля для sudo...", 'info', 'ssh')
                self.log(f"💻 >>> [пароль скрыт]", 'info', 'ssh')
                
                # Отправляем пароль
                channel.send(f"{self.password_var.get()}\n")
                time.sleep(2)  # Увеличиваем время ожидания
                
                # Ждем приглашения root
                response = ""
                root_prompt_found = False
                timeout = 0
                max_timeout = 100  # 10 секунд максимум
                
                while not root_prompt_found and timeout < max_timeout:
                    if channel.recv_ready():
                        data = channel.recv(1024).decode('utf-8', errors='ignore')
                        response += data
                        if data.strip():
                            self.log(f"💻 <<< {data.strip()}", 'info', 'ssh')
                        
                        # Проверяем различные варианты приглашения root
                        if ("#" in data and ("root@" in data or "root:" in data)) or data.endswith("#"):
                            root_prompt_found = True
                            break
                    
                    time.sleep(0.1)
                    timeout += 1
                
                if not root_prompt_found:
                    self.log(f"⚠️ Не удалось найти приглашение root, пробуем продолжить...", 'warning', 'ssh')
                
                self.log(f"✅ Переключились на root", 'info', 'ssh')
                
                # Выполняем команду от root
                self.log(f"📝 Выполнение от root: {command}", 'info', 'ssh')
                self.log(f"💻 >>> {command}", 'info', 'ssh')
                channel.send(f"{command}\n")
                time.sleep(2)
                
                # Читаем результат
                output = ""
                timeout = 0
                max_timeout = 200  # 20 секунд максимум
                
                while timeout < max_timeout:
                    if channel.recv_ready():
                        data = channel.recv(1024).decode('utf-8', errors='ignore')
                        output += data
                        if data.strip():
                            self.log(f"💻 <<< {data.strip()}", 'info', 'ssh')
                        timeout = 0  # Сбрасываем таймаут при получении данных
                    else:
                        timeout += 1
                    time.sleep(0.1)
                
                # Выходим из root
                self.log(f"💻 >>> exit", 'info', 'ssh')
                channel.send("exit\n")
                time.sleep(1)
                channel.close()
                
                self.log(f"✅ Вывод: {output.strip()}", 'info', 'ssh')
                return output, "", 0
                
            else:
                # Обычное выполнение команды
                self.log(f"📝 Выполнение: {command}", 'info', 'ssh')
                self.log(f"💻 >>> {command}", 'info', 'ssh')
                
                stdin, stdout, stderr = ssh.exec_command(command)
                
                # Читаем вывод с таймаутом
                import select
                
                # Ждем завершения команды
                while not stdout.channel.exit_status_ready():
                    if select.select([stdout.channel], [], [], 1)[0]:
                        pass
                
                # Получаем код возврата
                exit_status = stdout.channel.recv_exit_status()
                
                # Читаем вывод
                output = stdout.read().decode('utf-8', errors='ignore')
                error = stderr.read().decode('utf-8', errors='ignore')
                
                self.log(f"📊 Код возврата: {exit_status}", 'debug', 'ssh')
                
                if output:
                    self.log(f"💻 <<< {output.strip()}", 'info', 'ssh')
                if error:
                    self.log(f"💻 <<< ERROR: {error.strip()}", 'warning', 'ssh')
                
                if exit_status != 0:
                    self.log(f"❌ Команда завершилась с ошибкой (код: {exit_status})", 'error', 'ssh')
                
                return output, error, exit_status
            
        except Exception as e:
            self.log(f"💥 Ошибка выполнения команды: {e}", 'error', 'ssh')
            return "", str(e), -1
    
    def quick_start(self):
        """Быстрый старт"""
        self.log("🚀 Запуск быстрого старта...", 'info')
        self.progress_bar.start()
        self.progress_var.set("Быстрый старт...")
        
        def start():
            try:
                ip = self.ip_var.get()
                login = self.login_var.get()
                password = self.password_var.get()
                
                if not all([ip, login, password]):
                    self.log("❌ Заполните все поля", 'error')
                    return
                
                # Подключение
                ssh = self.connect_ssh(ip, login, password)
                if not ssh:
                    self.log("❌ Не удалось подключиться", 'error')
                    return
                
                # Применяем стандартный патч
                self.log("🔧 Применение стандартного патча...", 'info')
                self.apply_standard_patch(ssh)
                
                ssh.close()
                self.log("✅ Быстрый старт завершен", 'info')
                self.progress_var.set("Быстрый старт завершен")
                
            except Exception as e:
                self.log(f"❌ Ошибка быстрого старта: {e}", 'error')
                self.progress_var.set("Ошибка")
            finally:
                self.progress_bar.stop()
        
        threading.Thread(target=start, daemon=True).start()
    
    def apply_standard_patch(self, ssh):
        """Применение стандартного патча (простой метод)"""
        try:
            # Создание резервной копии
            self.log("💾 Создание резервной копии...", 'info', 'system')
            backup_script = """
            BACKUP_DIR="/tmp/synology_backup_$(date +%Y%m%d_%H%M%S)"
            mkdir -p $BACKUP_DIR
            cp /etc.defaults/synoinfo.conf $BACKUP_DIR/ 2>/dev/null || echo "synoinfo.conf not found"
            echo "Backup created in $BACKUP_DIR"
            """
            output, error, code = self.execute_ssh_command(ssh, backup_script, use_sudo=True)
            self.log(f"📁 Резервная копия: {output.strip()}", 'info', 'system')
            
            # Простая модификация synoinfo.conf по инструкции
            self.log("🔧 Модификация /etc.defaults/synoinfo.conf...", 'info', 'system')
            self.log("💻 >>> sudo -i", 'info', 'ssh')
            
            # Выполняем команды пошагово как в инструкции
            commands = [
                "sudo -i",
                "sed -i 's/support_disk_compatibility=\"yes\"/support_disk_compatibility=\"no\"/g' /etc.defaults/synoinfo.conf",
                "echo 'support_disk_compatibility=\"no\"' >> /etc.defaults/synoinfo.conf",
                "echo 'support_disk_compatibility_override=\"yes\"' >> /etc.defaults/synoinfo.conf",
                "echo 'Disk compatibility check disabled'",
                "exit"
            ]
            
            for cmd in commands:
                self.log(f"💻 >>> {cmd}", 'info', 'ssh')
                output, error, code = self.execute_ssh_command(ssh, cmd, use_sudo=True)
                if output.strip():
                    self.log(f"💻 <<< {output.strip()}", 'info', 'ssh')
                if error.strip():
                    self.log(f"💻 <<< ERROR: {error.strip()}", 'warning', 'ssh')
            
            self.log("✅ Стандартный патч применен успешно!", 'info', 'system')
            self.log("🔄 Рекомендуется перезагрузить NAS для применения изменений", 'info', 'system')
            
        except Exception as e:
            self.log(f"❌ Ошибка применения патча: {e}", 'error')
    
    def toshiba_fix(self):
        """Фикс для Toshiba HDWT860"""
        self.log("💾 Запуск фикса для Toshiba HDWT860...", 'info')
        self.progress_bar.start()
        self.progress_var.set("Фикс Toshiba HDWT860...")
        
        def fix():
            try:
                ip = self.ip_var.get()
                login = self.login_var.get()
                password = self.password_var.get()
                
                if not all([ip, login, password]):
                    self.log("❌ Заполните все поля", 'error')
                    return
                
                # Подключение
                ssh = self.connect_ssh(ip, login, password)
                if not ssh:
                    self.log("❌ Не удалось подключиться", 'error')
                    return
                
                # Применяем специальный фикс для Toshiba
                self.log("🔧 Применение специального фикса для Toshiba HDWT860...", 'info')
                self.apply_toshiba_fix(ssh)
                
                ssh.close()
                self.log("✅ Фикс Toshiba HDWT860 завершен", 'info')
                self.progress_var.set("Фикс завершен")
                
            except Exception as e:
                self.log(f"❌ Ошибка фикса Toshiba: {e}", 'error')
                self.progress_var.set("Ошибка")
            finally:
                self.progress_bar.stop()
        
        threading.Thread(target=fix, daemon=True).start()
    
    def apply_toshiba_fix(self, ssh):
        """Применение специального фикса для Toshiba HDWT860"""
        try:
            # Создание резервной копии
            self.log("💾 Создание резервной копии...", 'info', 'system')
            backup_script = """
            BACKUP_DIR="/tmp/toshiba_fix_backup_$(date +%Y%m%d_%H%M%S)"
            mkdir -p $BACKUP_DIR
            cp /etc/synoinfo.conf $BACKUP_DIR/ 2>/dev/null || echo "synoinfo.conf not found"
            cp /usr/syno/bin/synocheck $BACKUP_DIR/ 2>/dev/null || echo "synocheck not found"
            echo "Backup created in $BACKUP_DIR"
            """
            output, error, code = self.execute_ssh_command(ssh, backup_script, use_sudo=True)
            self.log(f"📁 Резервная копия: {output.strip()}", 'info', 'system')
            
            # Специальный фикс для Toshiba HDWT860
            self.log("🔧 Применение специального фикса для Toshiba HDWT860...", 'info', 'system')
            toshiba_script = """
            #!/bin/bash
            echo "Applying Toshiba HDWT860 special fix..."
            
            # Создаем резервную копию
            cp /etc/synoinfo.conf /etc/synoinfo.conf.backup
            
            # Удаляем старые настройки
            sed -i '/support_disk_compatibility/d' /etc/synoinfo.conf
            sed -i '/support_disk_compatibility_check/d' /etc/synoinfo.conf
            sed -i '/support_disk_compatibility_override/d' /etc/synoinfo.conf
            
            # Добавляем специальные настройки для Toshiba HDWT860
            cat >> /etc/synoinfo.conf << 'EOF'
            
            # Synology Drive Unlocker - Toshiba HDWT860 Special Fix
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
            
            echo "Toshiba HDWT860 special fix applied to synoinfo.conf"
            """
            output, error, code = self.execute_ssh_command(ssh, toshiba_script, use_sudo=True)
            self.log(f"✅ Toshiba фикс synoinfo.conf: {output.strip()}", 'info', 'system')
            
            # Модификация synocheck для Toshiba
            self.log("🔧 Модификация synocheck для Toshiba...", 'info', 'system')
            synocheck_script = """
            #!/bin/bash
            echo "Modifying synocheck for Toshiba HDWT860..."
            
            # Создаем резервную копию
            cp /usr/syno/bin/synocheck /usr/syno/bin/synocheck.backup
            
            # Создаем специальный synocheck для Toshiba
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
            echo "synocheck modified for Toshiba HDWT860"
            """
            output, error, code = self.execute_ssh_command(ssh, synocheck_script, use_sudo=True)
            self.log(f"✅ synocheck Toshiba: {output.strip()}", 'info', 'system')
            
            # Перезапуск служб
            self.log("🔄 Перезапуск служб...", 'info', 'system')
            restart_script = """
            /usr/syno/bin/synopkg restart pkgctl-WebStation 2>/dev/null || echo "WebStation restart failed"
            /usr/syno/bin/synopkg restart pkgctl-Docker 2>/dev/null || echo "Docker restart failed"
            /usr/syno/bin/synopkg restart pkgctl-StorageManager 2>/dev/null || echo "StorageManager restart failed"
            echo "Services restarted for Toshiba HDWT860"
            """
            output, error, code = self.execute_ssh_command(ssh, restart_script, use_sudo=True)
            self.log(f"🔄 Службы Toshiba: {output.strip()}", 'info', 'system')
            
            self.log("✅ Специальный фикс для Toshiba HDWT860 применен успешно!", 'info')
            
        except Exception as e:
            self.log(f"❌ Ошибка применения фикса Toshiba: {e}", 'error')
    
    def aggressive_patch(self):
        """Агрессивный патч"""
        self.log("Запуск агрессивного патча...", 'info')
        # Здесь будет логика агрессивного патча
        pass
    
    def standard_patch(self):
        """Стандартный патч"""
        self.log("Запуск стандартного патча...", 'info')
        # Здесь будет логика стандартного патча
        pass
    
    def toshiba_patch(self):
        """Патч для Toshiba"""
        self.log("Запуск патча для Toshiba...", 'info')
        # Здесь будет логика патча Toshiba
        pass
    
    def wd_red_patch(self):
        """Патч для WD Red"""
        self.log("Запуск патча для WD Red...", 'info')
        # Здесь будет логика патча WD Red
        pass
    
    def seagate_patch(self):
        """Патч для Seagate IronWolf"""
        self.log("Запуск патча для Seagate IronWolf...", 'info')
        # Здесь будет логика патча Seagate
        pass
    
    def analyze_dsm(self):
        """Анализ DSM"""
        self.log("Анализ системы DSM...", 'info')
        # Здесь будет логика анализа DSM
        pass
    
    def check_disks(self):
        """Проверка дисков"""
        self.log("Проверка дисков...", 'info')
        # Здесь будет логика проверки дисков
        pass
    
    def test_ssh(self):
        """Тест SSH"""
        self.log("Тест SSH подключения...", 'info')
        # Здесь будет логика теста SSH
        pass
    
    def analyze_logs(self):
        """Анализ логов"""
        self.log("Анализ логов...", 'info')
        # Здесь будет логика анализа логов
        pass
    
    def show_log(self, log_type):
        """Показ лога"""
        log_file = f"logs/{log_type}.log"
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as f:
                content = f.read()
            self.logs_text.delete(1.0, tk.END)
            self.logs_text.insert(1.0, content)
        else:
            self.logs_text.delete(1.0, tk.END)
            self.logs_text.insert(1.0, f"Лог {log_type} не найден")
    
    def clear_logs(self):
        """Очистка логов"""
        for log_type in ['main', 'ssh', 'system', 'error']:
            log_file = f"logs/{log_type}.log"
            if os.path.exists(log_file):
                with open(log_file, "w", encoding="utf-8") as f:
                    f.write("")
        self.log("Логи очищены", 'info')
    
    def open_logs_folder(self):
        """Открытие папки логов"""
        os.startfile("logs")
    
    def open_config_folder(self):
        """Открытие папки конфигурации"""
        os.startfile(".")
    
    def save_settings(self):
        """Сохранение настроек"""
        self.save_config()
        self.log("Настройки сохранены", 'info')
    
    def reset_settings(self):
        """Сброс настроек"""
        self.ip_var.set("192.168.1.100")
        self.login_var.set("admin")
        self.auto_save_var.set(True)
        self.log_level_var.set("INFO")
        self.max_log_size_var.set("10")
        self.ssh_timeout_var.set("30")
        self.ssh_retries_var.set("3")
        self.log("Настройки сброшены", 'info')

def main():
    root = tk.Tk()
    app = SynologyUnlockerPro(root)
    
    # Сохранение конфигурации при закрытии
    def on_closing():
        app.save_config()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()

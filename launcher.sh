#!/bin/bash
# Synology Drive Unlocker - Launcher для Linux/macOS
# Автоматический запуск утилиты с проверкой зависимостей

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция логирования
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Заголовок
echo
echo "========================================"
echo "    Synology Drive Unlocker v1.0"
echo "========================================"
echo

# Проверка наличия Python
log "Проверка Python..."
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        error "Python не найден! Установите Python 3.7+"
        echo "Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
        echo "CentOS/RHEL: sudo yum install python3 python3-pip"
        echo "macOS: brew install python3"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# Получение версии Python
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
log "Python $PYTHON_VERSION найден"

# Проверка pip
log "Проверка pip..."
if ! command -v pip3 &> /dev/null; then
    if ! command -v pip &> /dev/null; then
        error "pip не найден! Установите pip"
        echo "Ubuntu/Debian: sudo apt install python3-pip"
        echo "CentOS/RHEL: sudo yum install python3-pip"
        echo "macOS: brew install python3"
        exit 1
    else
        PIP_CMD="pip"
    fi
else
    PIP_CMD="pip3"
fi
log "pip найден"

# Проверка виртуального окружения
if [ ! -d "venv" ]; then
    log "Создание виртуального окружения..."
    $PYTHON_CMD -m venv venv
    if [ $? -ne 0 ]; then
        error "Не удалось создать виртуальное окружение"
        exit 1
    fi
    log "Виртуальное окружение создано"
fi

# Активация виртуального окружения
log "Активация виртуального окружения..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    error "Не удалось активировать виртуальное окружение"
    exit 1
fi

# Проверка и установка зависимостей
log "Проверка зависимостей..."
if ! $PIP_CMD list | grep -q paramiko; then
    log "Установка зависимостей..."
    $PIP_CMD install -r requirements.txt
    if [ $? -ne 0 ]; then
        error "Не удалось установить зависимости"
        exit 1
    fi
    log "Зависимости установлены"
else
    log "Зависимости уже установлены"
fi

# Проверка основного файла
if [ ! -f "synology_unlocker.py" ]; then
    error "Файл synology_unlocker.py не найден!"
    echo "Убедитесь, что вы находитесь в правильной директории"
    exit 1
fi

# Создание директорий
mkdir -p backups logs

# Проверка прав на выполнение скриптов
chmod +x scripts/*.sh 2>/dev/null || true

# Запуск приложения
echo
log "Запуск Synology Drive Unlocker..."
echo "========================================"
echo

$PYTHON_CMD synology_unlocker.py

# Обработка завершения
if [ $? -eq 0 ]; then
    echo
    log "Приложение завершено успешно"
    echo
else
    echo
    error "Приложение завершилось с ошибкой"
    echo
fi

#!/bin/bash
# Synology Drive Unlocker - Скрипт резервного копирования
# Создает резервные копии критически важных файлов

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция логирования
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Создание директории для резервных копий
BACKUP_DIR="/tmp/synology_backup_$(date +%Y%m%d_%H%M%S)"
log "Создание директории резервного копирования: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# Функция копирования файла с проверкой
copy_file() {
    local source="$1"
    local dest="$2"
    local description="$3"
    
    if [ -f "$source" ]; then
        cp "$source" "$dest" 2>/dev/null && log "✓ $description скопирован" || error "✗ Не удалось скопировать $description"
    else
        warning "Файл $source не найден"
    fi
}

# Функция копирования директории с проверкой
copy_dir() {
    local source="$1"
    local dest="$2"
    local description="$3"
    
    if [ -d "$source" ]; then
        cp -r "$source" "$dest" 2>/dev/null && log "✓ $description скопирована" || error "✗ Не удалось скопировать $description"
    else
        warning "Директория $source не найдена"
    fi
}

log "Начинаем создание резервной копии..."

# Копируем основные конфигурационные файлы
log "Копирование конфигурационных файлов..."

copy_file "/etc/synoinfo.conf" "$BACKUP_DIR/synoinfo.conf" "synoinfo.conf"
copy_file "/etc.defaults/synoinfo.conf" "$BACKUP_DIR/synoinfo.conf.defaults" "synoinfo.conf.defaults"
copy_file "/usr/syno/bin/synocheck" "$BACKUP_DIR/synocheck" "synocheck"

# Копируем дополнительные важные файлы
log "Копирование дополнительных файлов..."

copy_file "/etc/synoinfo.conf.backup" "$BACKUP_DIR/synoinfo.conf.backup" "synoinfo.conf.backup"
copy_file "/usr/syno/bin/synocheck.backup" "$BACKUP_DIR/synocheck.backup" "synocheck.backup"

# Копируем информацию о системе
log "Сохранение информации о системе..."

echo "=== Информация о системе ===" > "$BACKUP_DIR/system_info.txt"
echo "Дата создания резервной копии: $(date)" >> "$BACKUP_DIR/system_info.txt"
echo "Версия DSM: $(cat /etc.defaults/VERSION 2>/dev/null || echo 'Неизвестно')" >> "$BACKUP_DIR/system_info.txt"
echo "Модель: $(cat /proc/sys/kernel/syno_hw_version 2>/dev/null || echo 'Неизвестно')" >> "$BACKUP_DIR/system_info.txt"
echo "Архитектура: $(uname -m)" >> "$BACKUP_DIR/system_info.txt"
echo "Ядро: $(uname -r)" >> "$BACKUP_DIR/system_info.txt"

# Копируем информацию о дисках
echo "=== Информация о дисках ===" >> "$BACKUP_DIR/system_info.txt"
lsblk >> "$BACKUP_DIR/system_info.txt" 2>/dev/null || echo "lsblk недоступен" >> "$BACKUP_DIR/system_info.txt"

# Копируем логи системы
log "Копирование логов системы..."
copy_dir "/var/log" "$BACKUP_DIR/logs" "логи системы"

# Создаем архив резервной копии
log "Создание архива резервной копии..."
cd "$(dirname "$BACKUP_DIR")"
tar -czf "$(basename "$BACKUP_DIR").tar.gz" "$(basename "$BACKUP_DIR")" 2>/dev/null && log "✓ Архив создан" || error "✗ Не удалось создать архив"

# Показываем информацию о резервной копии
log "Информация о резервной копии:"
echo "  Директория: $BACKUP_DIR"
echo "  Размер: $(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)"
echo "  Файлов: $(find "$BACKUP_DIR" -type f | wc -l)"

# Создаем файл с инструкциями по восстановлению
cat > "$BACKUP_DIR/RESTORE_INSTRUCTIONS.txt" << 'EOF'
ИНСТРУКЦИИ ПО ВОССТАНОВЛЕНИЮ
============================

Для восстановления оригинальных настроек выполните следующие команды:

1. Восстановление synoinfo.conf:
   sudo cp synoinfo.conf /etc/synoinfo.conf

2. Восстановление synocheck:
   sudo cp synocheck /usr/syno/bin/synocheck
   sudo chmod +x /usr/syno/bin/synocheck

3. Перезапуск служб:
   sudo /usr/syno/bin/synopkg restart pkgctl-WebStation
   sudo /usr/syno/bin/synopkg restart pkgctl-Docker

4. Перезагрузка NAS:
   sudo reboot

ВНИМАНИЕ: Выполняйте команды с осторожностью!
EOF

log "✅ Резервная копия создана успешно!"
log "Расположение: $BACKUP_DIR"
log "Архив: $BACKUP_DIR.tar.gz"

# Сохраняем путь к резервной копии для последующего использования
echo "$BACKUP_DIR" > /tmp/last_backup_path

exit 0

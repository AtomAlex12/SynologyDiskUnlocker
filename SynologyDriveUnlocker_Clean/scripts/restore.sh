#!/bin/bash
# Synology Drive Unlocker - Скрипт восстановления
# Восстанавливает оригинальные настройки и ограничения

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Проверка прав root
if [ "$EUID" -ne 0 ]; then
    error "Этот скрипт должен быть запущен с правами root"
    exit 1
fi

log "Начинаем восстановление оригинальных настроек..."

# Функция восстановления файла из резервной копии
restore_file() {
    local file="$1"
    local backup_pattern="$2"
    local description="$3"
    
    # Ищем самую новую резервную копию
    local latest_backup=$(ls -t "$backup_pattern" 2>/dev/null | head -1)
    
    if [ -n "$latest_backup" ] && [ -f "$latest_backup" ]; then
        cp "$latest_backup" "$file" 2>/dev/null && log "✓ $description восстановлен из $latest_backup" || error "✗ Не удалось восстановить $description"
    else
        warning "Резервная копия для $description не найдена"
    fi
}

# Функция проверки существования файла
check_file() {
    local file="$1"
    if [ ! -f "$file" ]; then
        warning "Файл $file не найден"
        return 1
    fi
    return 0
}

# 1. Восстановление synoinfo.conf
log "Восстановление /etc/synoinfo.conf..."

if check_file "/etc/synoinfo.conf"; then
    restore_file "/etc/synoinfo.conf" "/etc/synoinfo.conf.backup.*" "synoinfo.conf"
    
    # Удаляем добавленные нами строки
    sed -i '/# Synology Drive Unlocker/d' /etc/synoinfo.conf
    sed -i '/support_disk_compatibility_override/d' /etc/synoinfo.conf
    sed -i '/support_disk_compatibility_force/d' /etc/synoinfo.conf
    
    # Восстанавливаем оригинальные настройки
    sed -i 's/support_disk_compatibility="no"/support_disk_compatibility="yes"/g' /etc/synoinfo.conf
    sed -i 's/support_disk_compatibility_check="no"/support_disk_compatibility_check="yes"/g' /etc/synoinfo.conf
    
    log "✓ /etc/synoinfo.conf восстановлен"
else
    error "Файл /etc/synoinfo.conf не найден"
fi

# 2. Восстановление synocheck
log "Восстановление /usr/syno/bin/synocheck..."

if check_file "/usr/syno/bin/synocheck"; then
    # Удаляем символическую ссылку на обертку
    if [ -L "/usr/syno/bin/synocheck" ]; then
        rm -f /usr/syno/bin/synocheck
        log "✓ Удалена символическая ссылка на обертку"
    fi
    
    # Восстанавливаем оригинальный файл
    if [ -f "/usr/syno/bin/synocheck.original" ]; then
        cp /usr/syno/bin/synocheck.original /usr/syno/bin/synocheck
        chmod +x /usr/syno/bin/synocheck
        log "✓ /usr/syno/bin/synocheck восстановлен из оригинальной копии"
    else
        restore_file "/usr/syno/bin/synocheck" "/usr/syno/bin/synocheck.backup.*" "synocheck"
    fi
else
    warning "Файл /usr/syno/bin/synocheck не найден"
fi

# 3. Восстановление /etc.defaults/synoinfo.conf
log "Восстановление /etc.defaults/synoinfo.conf..."

if check_file "/etc.defaults/synoinfo.conf"; then
    restore_file "/etc.defaults/synoinfo.conf" "/etc.defaults/synoinfo.conf.backup.*" "synoinfo.conf.defaults"
    
    # Восстанавливаем оригинальные настройки
    sed -i 's/support_disk_compatibility="no"/support_disk_compatibility="yes"/g' /etc.defaults/synoinfo.conf
    sed -i 's/support_disk_compatibility_check="no"/support_disk_compatibility_check="yes"/g' /etc.defaults/synoinfo.conf
    
    log "✓ /etc.defaults/synoinfo.conf восстановлен"
fi

# 4. Удаление созданных нами файлов и служб
log "Удаление созданных файлов и служб..."

# Удаляем службу systemd
if [ -f "/etc/systemd/system/synology-unlocker.service" ]; then
    systemctl stop synology-unlocker.service 2>/dev/null || true
    systemctl disable synology-unlocker.service 2>/dev/null || true
    rm -f /etc/systemd/system/synology-unlocker.service
    log "✓ Служба systemd удалена"
fi

# Удаляем скрипты
rm -f /usr/local/bin/disable_disk_checks.sh
rm -f /usr/local/bin/synocheck_wrapper.sh
log "✓ Созданные скрипты удалены"

# Удаляем резервные копии (опционально)
read -p "Удалить резервные копии? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -f /etc/synoinfo.conf.backup.*
    rm -f /usr/syno/bin/synocheck.backup.*
    rm -f /etc.defaults/synoinfo.conf.backup.*
    rm -f /usr/syno/bin/synocheck.original
    log "✓ Резервные копии удалены"
else
    log "✓ Резервные копии сохранены"
fi

# 5. Перезапуск служб
log "Перезапуск служб..."

# Перезапускаем основные службы
/usr/syno/bin/synopkg restart pkgctl-WebStation 2>/dev/null && log "✓ WebStation перезапущен" || warning "Не удалось перезапустить WebStation"
/usr/syno/bin/synopkg restart pkgctl-Docker 2>/dev/null && log "✓ Docker перезапущен" || warning "Не удалось перезапустить Docker"
/usr/syno/bin/synopkg restart pkgctl-StorageManager 2>/dev/null && log "✓ StorageManager перезапущен" || warning "Не удалось перезапустить StorageManager"

# 6. Проверка восстановления
log "Проверка восстановления..."

info "Проверка synoinfo.conf:"
grep -i "support_disk_compatibility" /etc/synoinfo.conf | tail -5

info "Проверка synocheck:"
ls -la /usr/syno/bin/synocheck*

# 7. Создание отчета о восстановлении
log "Создание отчета о восстановлении..."

report_file="/tmp/synology_unlocker_restore_report_$(date +%Y%m%d_%H%M%S).txt"
cat > "$report_file" << EOF
ОТЧЕТ О ВОССТАНОВЛЕНИИ
=====================
Дата: $(date)
Версия DSM: $(cat /etc.defaults/VERSION 2>/dev/null || echo 'Неизвестно')
Модель: $(cat /proc/sys/kernel/syno_hw_version 2>/dev/null || echo 'Неизвестно')

ВЫПОЛНЕННЫЕ ДЕЙСТВИЯ:
- Восстановлен /etc/synoinfo.conf
- Восстановлен /usr/syno/bin/synocheck
- Восстановлен /etc.defaults/synoinfo.conf
- Удалены созданные скрипты и службы
- Перезапущены основные службы

СТАТУС ФАЙЛОВ:
$(ls -la /etc/synoinfo.conf /usr/syno/bin/synocheck /etc.defaults/synoinfo.conf 2>/dev/null)

РЕКОМЕНДАЦИИ:
1. Перезагрузите NAS для полного применения изменений
2. Проверьте, что ограничения на диски восстановлены
3. Убедитесь, что система работает стабильно

EOF

log "✓ Отчет создан: $report_file"

log "✅ Восстановление завершено успешно!"
log "Рекомендуется перезагрузить NAS для полного применения изменений"

# Предложение перезагрузки
read -p "Перезагрузить NAS сейчас? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log "Перезагрузка NAS через 5 секунд..."
    sleep 5
    reboot
else
    log "Перезагрузка отменена. Выполните перезагрузку вручную."
fi

exit 0

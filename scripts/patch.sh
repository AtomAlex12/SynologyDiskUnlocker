#!/bin/bash
# Synology Drive Unlocker - Скрипт применения патча
# Обходит ограничения на использование несертифицированных дисков

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

log "Начинаем применение патча для обхода ограничений дисков..."

# Функция создания резервной копии файла
backup_file() {
    local file="$1"
    if [ -f "$file" ]; then
        cp "$file" "$file.backup.$(date +%Y%m%d_%H%M%S)" 2>/dev/null && log "✓ Создана резервная копия $file" || warning "Не удалось создать резервную копию $file"
    fi
}

# Функция проверки существования файла
check_file() {
    local file="$1"
    if [ ! -f "$file" ]; then
        error "Файл $file не найден"
        return 1
    fi
    return 0
}

# 1. Модификация synoinfo.conf
log "Модификация /etc/synoinfo.conf..."

if check_file "/etc/synoinfo.conf"; then
    backup_file "/etc/synoinfo.conf"
    
    # Отключаем проверки совместимости дисков
    sed -i 's/support_disk_compatibility="yes"/support_disk_compatibility="no"/g' /etc/synoinfo.conf
    sed -i 's/support_disk_compatibility_check="yes"/support_disk_compatibility_check="no"/g' /etc/synoinfo.conf
    
    # Добавляем дополнительные настройки
    echo "" >> /etc/synoinfo.conf
    echo "# Synology Drive Unlocker - Обход ограничений дисков" >> /etc/synoinfo.conf
    echo "support_disk_compatibility=\"no\"" >> /etc/synoinfo.conf
    echo "support_disk_compatibility_check=\"no\"" >> /etc/synoinfo.conf
    echo "support_disk_compatibility_override=\"yes\"" >> /etc/synoinfo.conf
    echo "support_disk_compatibility_force=\"yes\"" >> /etc/synoinfo.conf
    
    log "✓ /etc/synoinfo.conf модифицирован"
else
    error "Не удалось найти /etc/synoinfo.conf"
    exit 1
fi

# 2. Модификация synocheck
log "Модификация /usr/syno/bin/synocheck..."

if check_file "/usr/syno/bin/synocheck"; then
    backup_file "/usr/syno/bin/synocheck"
    
    # Создаем временный файл с модифицированным synocheck
    temp_file="/tmp/synocheck_patched"
    
    # Копируем оригинальный файл
    cp /usr/syno/bin/synocheck "$temp_file"
    
    # Отключаем проверки совместимости дисков
    sed -i 's/check_disk_compatibility/return 0 # check_disk_compatibility/g' "$temp_file"
    
    # Заменяем оригинальный файл
    mv "$temp_file" /usr/syno/bin/synocheck
    chmod +x /usr/syno/bin/synocheck
    
    log "✓ /usr/syno/bin/synocheck модифицирован"
else
    warning "Файл /usr/syno/bin/synocheck не найден, пропускаем"
fi

# 3. Модификация дополнительных файлов
log "Проверка дополнительных файлов..."

# Проверяем и модифицируем /etc.defaults/synoinfo.conf
if [ -f "/etc.defaults/synoinfo.conf" ]; then
    backup_file "/etc.defaults/synoinfo.conf"
    
    sed -i 's/support_disk_compatibility="yes"/support_disk_compatibility="no"/g' /etc.defaults/synoinfo.conf
    sed -i 's/support_disk_compatibility_check="yes"/support_disk_compatibility_check="no"/g' /etc.defaults/synoinfo.conf
    
    log "✓ /etc.defaults/synoinfo.conf модифицирован"
fi

# 4. Создание дополнительных скриптов
log "Создание дополнительных скриптов..."

# Скрипт для отключения проверок при загрузке
cat > /usr/local/bin/disable_disk_checks.sh << 'EOF'
#!/bin/bash
# Отключение проверок дисков при загрузке

# Отключаем проверки в synoinfo.conf
sed -i 's/support_disk_compatibility="yes"/support_disk_compatibility="no"/g' /etc/synoinfo.conf
sed -i 's/support_disk_compatibility_check="yes"/support_disk_compatibility_check="no"/g' /etc/synoinfo.conf

# Убеждаемся, что настройки применены
echo "support_disk_compatibility=\"no\"" >> /etc/synoinfo.conf
echo "support_disk_compatibility_check=\"no\"" >> /etc/synoinfo.conf
EOF

chmod +x /usr/local/bin/disable_disk_checks.sh

# 5. Создание службы для автоматического применения патча
log "Создание службы для автоматического применения патча..."

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

# Включаем службу
systemctl enable synology-unlocker.service 2>/dev/null || warning "Не удалось включить службу systemd"

# 6. Применение дополнительных патчей
log "Применение дополнительных патчей..."

# Отключаем проверки в других местах
if [ -f "/usr/syno/bin/synocheck" ]; then
    # Создаем обертку для synocheck
    cat > /usr/local/bin/synocheck_wrapper.sh << 'EOF'
#!/bin/bash
# Обертка для synocheck, отключающая проверки дисков

# Если это проверка дисков, возвращаем успех
if [[ "$*" == *"disk"* ]] || [[ "$*" == *"compatibility"* ]]; then
    echo "Disk compatibility check bypassed by Synology Drive Unlocker"
    exit 0
fi

# Иначе запускаем оригинальный synocheck
exec /usr/syno/bin/synocheck.original "$@"
EOF

    chmod +x /usr/local/bin/synocheck_wrapper.sh
    
    # Создаем резервную копию оригинального synocheck
    if [ ! -f "/usr/syno/bin/synocheck.original" ]; then
        cp /usr/syno/bin/synocheck /usr/syno/bin/synocheck.original
    fi
    
    # Заменяем synocheck на обертку
    mv /usr/syno/bin/synocheck /usr/syno/bin/synocheck.backup
    ln -sf /usr/local/bin/synocheck_wrapper.sh /usr/syno/bin/synocheck
    
    log "✓ Создана обертка для synocheck"
fi

# 7. Очистка временных файлов
log "Очистка временных файлов..."
rm -f /tmp/synocheck_patched

# 8. Проверка примененных изменений
log "Проверка примененных изменений..."

info "Проверка synoinfo.conf:"
grep -i "support_disk_compatibility" /etc/synoinfo.conf | tail -5

info "Проверка synocheck:"
ls -la /usr/syno/bin/synocheck*

# 9. Создание отчета
log "Создание отчета о применении патча..."

report_file="/tmp/synology_unlocker_report_$(date +%Y%m%d_%H%M%S).txt"
cat > "$report_file" << EOF
ОТЧЕТ О ПРИМЕНЕНИИ ПАТЧА
========================
Дата: $(date)
Версия DSM: $(cat /etc.defaults/VERSION 2>/dev/null || echo 'Неизвестно')
Модель: $(cat /proc/sys/kernel/syno_hw_version 2>/dev/null || echo 'Неизвестно')

ВЫПОЛНЕННЫЕ ДЕЙСТВИЯ:
- Модифицирован /etc/synoinfo.conf
- Модифицирован /usr/syno/bin/synocheck
- Создана обертка для synocheck
- Создана служба systemd
- Созданы резервные копии

ФАЙЛЫ РЕЗЕРВНЫХ КОПИЙ:
$(find /etc /usr/syno/bin -name "*.backup.*" 2>/dev/null | head -10)

РЕКОМЕНДАЦИИ:
1. Перезагрузите NAS для применения изменений
2. Проверьте, что диски определяются без предупреждений
3. Сохраните этот отчет для возможного восстановления

EOF

log "✓ Отчет создан: $report_file"

log "✅ Патч применен успешно!"
log "Рекомендуется перезагрузить NAS для применения изменений"

exit 0

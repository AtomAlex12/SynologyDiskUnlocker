# Synology Drive Unlocker - Исходный код

## Описание
Исходный код утилиты для разблокировки несовместимых дисков на Synology NAS.

## Структура проекта

### Основные файлы
- `synology_unlocker_final.py` - Финальная версия (для exe)
- `synology_unlocker_simple.py` - Простая версия
- `synology_unlocker_pro.py` - PRO версия с расширенными функциями

### Скрипты сборки
- `build_exe.py` - Сборка exe файла
- `create_icon.py` - Создание иконки
- `build.bat` - Батник для сборки

### Запуск
- `synology_simple.bat` - Запуск простой версии
- `synology_pro.bat` - Запуск PRO версии
- `install.bat` - Установка зависимостей

### Документация
- `README.md` - Основная документация
- `RELEASE_README.md` - Документация для релиза

## Требования для разработки

```bash
pip install -r requirements.txt
```

## Сборка exe

```bash
python build_exe.py
```

## Лицензия
MIT License

## Автор
Synology Drive Unlocker Team

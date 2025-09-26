#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Создание иконки для Synology Drive Unlocker
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    """Создание иконки"""
    print("🎨 Создание иконки...")
    
    # Размеры иконки
    size = 256
    
    # Создаем изображение
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Фон
    draw.ellipse([10, 10, size-10, size-10], fill=(0, 100, 200, 255), outline=(0, 150, 255, 255), width=4)
    
    # Символ разблокировки
    # Замок
    lock_x = size // 2 - 30
    lock_y = size // 2 - 20
    draw.rectangle([lock_x, lock_y, lock_x + 60, lock_y + 40], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=2)
    
    # Дужка замка
    draw.arc([lock_x - 10, lock_y - 10, lock_x + 70, lock_y + 30], 0, 180, fill=(255, 255, 255, 255), width=4)
    
    # Ключ
    key_x = size // 2 + 40
    key_y = size // 2
    draw.rectangle([key_x, key_y - 5, key_x + 20, key_y + 5], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=2)
    draw.ellipse([key_x + 15, key_y - 8, key_x + 25, key_y + 8], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=2)
    
    # Текст
    try:
        # Пытаемся использовать системный шрифт
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 24)
        except:
            font = ImageFont.load_default()
    
    text = "SDU"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    text_x = (size - text_width) // 2
    text_y = size - 60
    
    draw.text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font)
    
    # Сохраняем иконку
    img.save('icon.ico', format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print("✅ Иконка создана: icon.ico")
    
    # Также создаем PNG версию
    img.save('icon.png', format='PNG')
    print("✅ PNG версия создана: icon.png")

if __name__ == "__main__":
    try:
        create_icon()
    except ImportError:
        print("❌ Pillow не установлен. Устанавливаем...")
        import subprocess
        import sys
        subprocess.run([sys.executable, "-m", "pip", "install", "Pillow"], check=True)
        print("✅ Pillow установлен. Повторяем создание иконки...")
        create_icon()
    except Exception as e:
        print(f"❌ Ошибка создания иконки: {e}")
        print("⚠️ Продолжаем без иконки...")

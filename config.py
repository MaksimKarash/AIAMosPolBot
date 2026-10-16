import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# Получаем токен
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Проверка: если токена нет — ошибка сразу
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env! Создай файл .env и добавь токен.")
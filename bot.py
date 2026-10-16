# ═══════════════════════════════════════════════════════════════
# bot.py — точка входа бота-ассистента первокурсника
# Разработчик 1: ядро бота и запуск
# ═══════════════════════════════════════════════════════════════

#Тестирую гит

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from config import BOT_TOKEN

# ═══════════════════════════════════════════════════════════════
# ШАГ 4.1 — Логирование
# ═══════════════════════════════════════════════════════════════
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# ═══════════════════════════════════════════════════════════════
# ШАГ 4.2 — Инициализация бота и диспетчера (без прокси)
# ═══════════════════════════════════════════════════════════════
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# ═══════════════════════════════════════════════════════════════
# ШАГ 5 — Временные обработчики /start и /help
# ═══════════════════════════════════════════════════════════════

@dp.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Обработчик команды /start."""
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n"
        "Я — ассистент первокурсника Московского Политеха.\n"
        "Выбери категорию или задай вопрос:"
    )


@dp.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Обработчик команды /help."""
    await message.answer(
        "Я помогу найти ответ на вопросы о:\n"
        "📍 Навигации по кампусу\n"
        "📚 Учёбе\n"
        "🏠 Общежитии\n"
        "💰 Стипендии\n"
        "📋 Административных вопросах\n\n"
        "Просто выбери категорию из меню."
    )

# ═══════════════════════════════════════════════════════════════
# ШАГ 6 — Подключение роутеров (пока закомментировано)
# ═══════════════════════════════════════════════════════════════
# from handlers import router as handlers_router
# dp.include_router(handlers_router)

# ═══════════════════════════════════════════════════════════════
# ШАГ 4.3 — Точка входа
# ═══════════════════════════════════════════════════════════════

async def main() -> None:
    """Запуск бота в режиме polling."""
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")
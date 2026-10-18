# handlers.py
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from questions import QUESTIONS
from keyboards import get_main_menu, get_category_menu, get_answer_menu
from logger import logger

router = Router()

# 1. Команда /start
@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n"
        "Я — ассистент первокурсника.\nВыбери категорию:",
        reply_markup=get_main_menu()
    )

# 2. Обработка нажатия на категорию (cat_Навигация, cat_Учёба и т.д.)
@router.callback_query(F.data.startswith("cat_"))
async def show_category(callback: CallbackQuery) -> None:
    category = callback.data.split("_", 1)[1] # Получаем название категории
    await callback.message.edit_text(
        f"Выбери вопрос по теме <b>«{category}»</b>:",
        reply_markup=get_category_menu(category)
    )
    await callback.answer()

# 3. Обработка нажатия на вопрос (вывод ответа)
@router.callback_query(F.data.startswith("q_"))
async def show_answer(callback: CallbackQuery) -> None:
    q_id = callback.data[2:] 
    
    if q_id in QUESTIONS:
        q = QUESTIONS[q_id]
        logger.info(f"User {callback.from_user.id} asked: {q['question']}")
        
        text = (
            f"📖 <b>{q['question']}</b>\n\n"
            f"{q['answer']}\n\n"
            f"<i>Источник: {q['source']}</i>"
        )
        await callback.message.edit_text(text, reply_markup=get_answer_menu(q['category']))
    else:
        await callback.message.answer("Вопрос не найден.")
    
    await callback.answer()

# 4. Кнопка "В главное меню"
@router.callback_query(F.data == "to_main")
async def back_to_main(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "Главное меню:\nВыбери категорию:", 
        reply_markup=get_main_menu()
    )
    await callback.answer()

# 5. Кнопка "Помощь"
@router.callback_query(F.data == "help")
async def help_callback(callback: CallbackQuery) -> None:
    await callback.message.answer("Нажми на кнопку с нужной категорией, чтобы найти ответ.")
    await callback.answer()

# 6. Команда /help
@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer("Выбери категорию из меню выше.", reply_markup=get_main_menu())

# 7. Fallback (если пишут текст)
@router.message()
async def fallback(message: Message) -> None:
    await message.answer("Я не понял вопрос 🤔\nПожалуйста, выбери категорию из меню.", reply_markup=get_main_menu())
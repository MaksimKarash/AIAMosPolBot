# handlers.py
import os
from collections import Counter
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from aiogram.enums import ChatAction

# Импортируем наши модули
from questions import QUESTIONS
from keyboards import get_main_menu, get_category_menu, get_answer_menu
from logger import logger, feedback_logger
from ai_client import ask_ai
from prompts import SYSTEM_PROMPT

router = Router()

# ═══════════════════════════════════════════════════════════════
# 1. КОМАНДЫ
# ═══════════════════════════════════════════════════════════════

@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n"
        "Я — ассистент первокурсника.\nВыбери категорию:",
        reply_markup=get_main_menu()
    )

@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "Я умею отвечать двумя способами:\n\n"
        "1️⃣ Нажми на кнопку с нужной категорией (Учёба, Навигация и т.д.), чтобы найти готовый ответ.\n"
        "2️⃣ Или просто напиши свой вопрос текстом прямо в чат (например: «Как получить справку?»), и я постараюсь ответить с помощью нейросети!",
        reply_markup=get_main_menu()
    )

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    ADMIN_ID = 123456789 # <-- Замени на свой ID
    
    if message.from_user.id != ADMIN_ID:
        await message.answer("Эта команда доступна только администратору.")
        return

    try:
        if not os.path.exists('feedback_logs.txt'):
            await message.answer("Файл с логами еще не создан.")
            return

        with open('feedback_logs.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        up_votes = 0
        down_votes = 0
        bad_questions_ids = []
        
        for line in lines:
            if "поставил 👍" in line:
                up_votes += 1
            elif "поставил 👎" in line:
                down_votes += 1
                q_id = None
                if "'" in line:
                    q_id = line.split("'")[1]
                elif '"' in line:
                    q_id = line.split('"')[1]
                if q_id:
                    bad_questions_ids.append(q_id)
                
        total = up_votes + down_votes
        if total == 0:
            await message.answer("Пока нет ни одной оценки.")
            return
            
        percent = int((up_votes / total) * 100)
        text = (
            f"📊 <b>Статистика оценок:</b>\n\n"
            f"Всего оценок: {total}\n"
            f"👍 Помогло: {up_votes} ({percent}%)\n"
            f"👎 Не помогло: {down_votes}\n\n"
        )
        
        if bad_questions_ids:
            text += "⚠️ <b>Топ проблемных вопросов:</b>\n"
            counter = Counter(bad_questions_ids)
            top_3 = counter.most_common(3) 
            for q_id, count in top_3:
                if q_id not in QUESTIONS:
                    continue
                q_text = QUESTIONS[q_id]["question"]
                if len(q_text) > 40:
                    q_text = q_text[:37] + "..."
                text += f"• {q_text} — {count} 👎\n"
        else:
            text += "🎉 Отлично! Пока нет ни одного вопроса с 👎.\n"
            
        if percent >= 80:
            text += "\n🔥 Отличный результат!"
        elif percent >= 50:
            text += "\n🙂 Хорошо, но есть куда расти."
        else:
            text += "\n⚠️ Внимание! Надо доработать вопросы."
            
        await message.answer(text)
    except Exception as e:
        await message.answer(f"Ошибка: {e}")

# ═══════════════════════════════════════════════════════════════
# 2. КНОПКИ КАТЕГОРИЙ И ВОПРОСОВ (CALLBACK)
# ═══════════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith("cat_"))
async def show_category(callback: CallbackQuery) -> None:
    category = callback.data.split("_", 1)[1]
    await callback.message.edit_text(
        f"Выбери вопрос по теме <b>«{category}»</b>:",
        reply_markup=get_category_menu(category)
    )
    await callback.answer()

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
        await callback.message.edit_text(text, reply_markup=get_answer_menu(q['category'], q_id))
    else:
        await callback.message.answer("Вопрос не найден.")
    await callback.answer()

@router.callback_query(F.data.startswith("rate_"))
async def handle_rating(callback: CallbackQuery) -> None:
    data = callback.data.split("_", 2)
    rating_type = data[1] 
    question_id = data[2] 
    
    if question_id not in QUESTIONS:
        await callback.answer("Этот вопрос устарел. Вызовите меню заново: /start", show_alert=True)
        return

    username = callback.from_user.username or callback.from_user.first_name
    
    if rating_type == "up":
        feedback_logger.info(f"@{username} поставил 👍 вопросу '{question_id}'")
        await callback.answer("Спасибо за оценку! Рад, что помог 😊")
    else:
        feedback_logger.info(f"@{username} поставил 👎 вопросу '{question_id}'")
        await callback.answer("Спасибо за фидбек! Мы поработаем над этим 🛠")
    
    try:
        current_markup = callback.message.reply_markup
        if current_markup and current_markup.inline_keyboard:
            new_keyboard = current_markup.inline_keyboard[1:] 
            new_markup = InlineKeyboardMarkup(inline_keyboard=new_keyboard)
            await callback.message.edit_reply_markup(reply_markup=new_markup)
    except Exception:
        pass

@router.callback_query(F.data.startswith("back_"))
async def back_to_category(callback: CallbackQuery) -> None:
    category = callback.data.split("_", 1)[1] 
    await callback.message.edit_text(
        f"Выбери вопрос по теме '{category}':", 
        reply_markup=get_category_menu(category)
    )
    await callback.answer()

@router.callback_query(F.data == "to_main")
async def back_to_main(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "Главное меню:\nВыбери категорию:", 
        reply_markup=get_main_menu()
    )
    await callback.answer()

@router.callback_query(F.data == "help")
async def help_callback(callback: CallbackQuery) -> None:
    await callback.message.answer(
        "Я умею отвечать двумя способами:\n\n"
        "1️⃣ Нажми на кнопку с нужной категорией, чтобы найти готовый ответ.\n"
        "2️⃣ Или просто напиши свой вопрос текстом прямо в чат, и я постараюсь ответить с помощью нейросети!"
    )
    await callback.answer()

# ═══════════════════════════════════════════════════════════════
# 3. ОБРАБОТЧИК ИИ (Должен быть ВЫШЕ Fallback!)
# ═══════════════════════════════════════════════════════════════
# Ловит весь текст, КРОМЕ команд (начинающихся с /)

@router.message(F.text & ~F.text.startswith('/'))
async def handle_free_text(message: Message):
    """Ловит любой текст, который не подошел под кнопки, и отправляет ИИ"""
    
    # Показываем, что бот "печатает"
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    
    thinking_msg = await message.answer("🤔 Думаю над твоим вопросом...")
    
    # Запрашиваем ответ у нейросети
    ai_response = await ask_ai(question=message.text, system_prompt=SYSTEM_PROMPT)
    
    await thinking_msg.delete()
    await message.answer(ai_response)

# ═══════════════════════════════════════════════════════════════
# 4. FALLBACK (САМЫЙ ПОСЛЕДНИЙ ОБРАБОТЧИК В ФАЙЛЕ!)
# ═══════════════════════════════════════════════════════════════
# Ловит всё остальное: стикеры, фото, гифки, неизвестные команды

@router.message()
async def fallback(message: Message) -> None:
    await message.answer(
        "Я не понял вопрос 🤔\n"
        "Пожалуйста, выбери категорию из меню ниже или напиши свой вопрос текстом.",
        reply_markup=get_main_menu()
    )

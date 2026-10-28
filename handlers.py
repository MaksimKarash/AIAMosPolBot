# handlers.py
import os
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from questions import QUESTIONS
from keyboards import get_main_menu, get_category_menu, get_answer_menu
from logger import logger
from aiogram.types import InlineKeyboardMarkup
from logger import feedback_logger

from collections import Counter
from questions import QUESTIONS

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
        await callback.message.edit_text(text, reply_markup=get_answer_menu(q['category'], q_id))
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



# 6. Обработка оценок 👍 / 👎
@router.callback_query(F.data.startswith("rate_"))
async def handle_rating(callback: CallbackQuery) -> None:
    # Получаем данные из callback (например, "rate_up_library")
     # maxsplit=2 означает: разбить только по первым двум подчеркиваниям
    data = callback.data.split("_", 2)
    rating_type = data[1] # "up" или "down"
    question_id = data[2] # ID вопроса
    
    username = callback.from_user.username or callback.from_user.first_name
    
    # Записываем в лог
    if rating_type == "up":
        feedback_logger.info(f"@{username} поставил 👍 вопросу '{question_id}'")
        await callback.answer("Спасибо за оценку! Рад, что помог 😊")
    else:
        feedback_logger.info(f"@{username} поставил 👎 вопросу '{question_id}'")
        await callback.answer("Спасибо за фидбек! Мы поработаем над этим вопросом 🛠")
    
    # Убираем кнопки оценок из сообщения, чтобы нельзя было нажать дважды
    try:
        # Берем текущую клавиатуру и удаляем первые две кнопки (оценки)
        current_markup = callback.message.reply_markup
        if current_markup and current_markup.inline_keyboard:
            # Оставляем только навигацию (кнопки "Назад" и "В меню")
            new_keyboard = current_markup.inline_keyboard[1:] 
            new_markup = InlineKeyboardMarkup(inline_keyboard=new_keyboard)
            await callback.message.edit_reply_markup(reply_markup=new_markup)
    except Exception as e:
        print(f"Не удалось обновить клавиатуру: {e}")

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    ADMIN_ID = 876899591 # <-- Твой ID
    
    if message.from_user.id != ADMIN_ID:
        await message.answer("Эта команда доступна только администратору.")
        return

    try:
        if not os.path.exists('feedback_logs.txt'):
            await message.answer("Файл с логами еще не создан. Никто пока не ставил оценки.")
            return

        with open('feedback_logs.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        up_votes = 0
        down_votes = 0
        bad_questions_ids = []
        
        # 1. Сначала полностью читаем файл
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
        
        # 2. А теперь проверяем, есть ли плохие вопросы
        if bad_questions_ids:
            text += "⚠️ <b>Топ проблемных вопросов (чаще всего 👎):</b>\n"
            counter = Counter(bad_questions_ids)
            top_3 = counter.most_common(3) 
            
            for q_id, count in top_3:
                if q_id not in QUESTIONS:
                    text += f"• Неизвестный ID: {q_id} — {count} 👎\n"
                    continue
                    
                q_text = QUESTIONS[q_id]["question"]
                if len(q_text) > 40:
                    q_text = q_text[:37] + "..."
                text += f"• {q_text} — {count} 👎\n"
        else:
            text += "🎉 Отлично! Пока нет ни одного вопроса, который получил бы 👎.\n"
            
        # 3. Добавляем финальную оценку (в самом конце)
        if percent >= 80:
            text += "\n🔥 Отличный результат! Пользователи очень довольны."
        elif percent >= 50:
            text += "\n🙂 Хорошо, но есть куда расти."
        else:
            text += "\n⚠️ Внимание! Много недовольных. Надо доработать вопросы."
            
        await message.answer(text)
        
    except Exception as e:
        await message.answer(f"Ошибка при чтении статистики: {e}")

# 7. Fallback (если пишут текст)
@router.message()
async def fallback(message: Message) -> None:
    await message.answer("Я не понял вопрос 🤔\nПожалуйста, выбери категорию из меню.", reply_markup=get_main_menu())
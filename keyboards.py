# keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from questions import get_by_category

def get_main_menu() -> InlineKeyboardMarkup:
    """Главное меню (кнопки под сообщением)"""
    keyboard = [
        [
            InlineKeyboardButton(text="📍 Навигация", callback_data="cat_Навигация"),
            InlineKeyboardButton(text="📚 Учёба", callback_data="cat_Учёба")
        ],
        [
            InlineKeyboardButton(text="🏠 Общежитие", callback_data="cat_Общежитие"),
            InlineKeyboardButton(text="💰 Стипендия", callback_data="cat_Стипендия")
        ],
        [
            InlineKeyboardButton(text="📋 Документы", callback_data="cat_Административное"),
            InlineKeyboardButton(text="🆘 Помощь", callback_data="help")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_category_menu(category: str) -> InlineKeyboardMarkup:
    """Список вопросов внутри категории"""
    category_questions = get_by_category(category)
    keyboard = []
    
    for q_id, q_data in category_questions.items():
        # Обрезаем слишком длинные вопросы для кнопок
        text = q_data["question"] if len(q_data["question"]) < 40 else q_data["question"][:37] + "..."
        keyboard.append([InlineKeyboardButton(text=text, callback_data=f"q_{q_id}")])
        
    # Кнопка возврата в главное меню
    keyboard.append([InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="to_main")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_answer_menu(category: str) -> InlineKeyboardMarkup:
    """Кнопки под ответом"""
    keyboard = [
        [InlineKeyboardButton(text="⬅️ Назад к вопросам", callback_data=f"cat_{category}")],
        [InlineKeyboardButton(text="🏠 В главное меню", callback_data="to_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
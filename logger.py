# logger.py
import logging

logging.basicConfig(
    filename='bot_logs.txt',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    encoding='utf-8'
)

logger = logging.getLogger(__name__)

# Создаем отдельный логгер для оценок
feedback_logger = logging.getLogger('feedback')
feedback_handler = logging.FileHandler('feedback_logs.txt', encoding='utf-8')
feedback_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
feedback_logger.addHandler(feedback_handler)
feedback_logger.setLevel(logging.INFO)
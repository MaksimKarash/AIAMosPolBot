# logger.py
import logging

logging.basicConfig(
    filename='bot_logs.txt',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    encoding='utf-8'
)

logger = logging.getLogger(__name__)
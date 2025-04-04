import logging
from datetime import datetime
from pathlib import Path
from config import Config

# Создаем директорию для логов если ее нет
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def log_error(message: str):
    """Логирование ошибок"""
    logger.error(f"ERROR: {message}")

def log_info(message: str):
    """Логирование информационных сообщений"""
    logger.info(f"INFO: {message}")

def log_debug(message: str):
    """Логирование отладочной информации"""
    if Config.DEBUG:
        logger.debug(f"DEBUG: {message}")
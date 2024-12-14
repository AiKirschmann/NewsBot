import sys
import os
from loguru import logger
from datetime import datetime

def setup_logger(name: str = None):
    """
    Настройка логгера
    Args:
        name: имя логгера (обычно __name__)
    Returns:
        настроенный логгер
    """
    # Создаем директорию для логов если её нет
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Формируем имя файла лога
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f")
    log_file = os.path.join(log_dir, f"newsbot.{current_time}.log")
    
    # Конфигурация логгера
    config = {
        "handlers": [
            {"sink": sys.stdout, "format": "{time} | {level} | {message}"},
            {"sink": log_file, "format": "{time} | {level} | {message}"}
        ]
    }
    
    # Очищаем предыдущие обработчики
    logger.remove()
    
    # Применяем новую конфигурацию
    for handler in config["handlers"]:
        logger.add(**handler)
    
    if name:
        return logger.bind(name=name)
    return logger

# Создаем глобальный логгер
default_logger = setup_logger("newsbot")

# Экспортируем функцию для использования в других модулях
__all__ = ["setup_logger", "default_logger"]

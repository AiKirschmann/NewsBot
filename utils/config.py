import os
from dataclasses import dataclass
from typing import List, Dict
from dotenv import load_dotenv
from utils.logger import default_logger as logger

@dataclass
class Config:
    """Конфигурация приложения"""
    # Базовые настройки
    TELEGRAM_TOKEN: str
    CHANNEL_ID: str
    ADMIN_ID: str
    DATABASE_URL: str
    
    # Дополнительные настройки
    NEWS_SOURCES: Dict
    RSS_SETTINGS: Dict
    PUBLISH_TIMES: List[str]
    POSTS_PER_TIME: int
    LOGGING_CONFIG: Dict

def load_config() -> Config:
    """Загружает конфигурацию из переменных окружения и возвращает объект Config"""
    # Загружаем переменные окружения
    load_dotenv()
    
    # Проверяем наличие обязательных переменных
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    channel_id = os.getenv('CHANNEL_ID')
    admin_id = os.getenv('ADMIN_ID')
    database_url = os.getenv('DATABASE_URL')
    
    required_vars = {
        'TELEGRAM_TOKEN': telegram_token,
        'CHANNEL_ID': channel_id,
        'ADMIN_ID': admin_id,
        'DATABASE_URL': database_url
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    # Настройки RSS источников
    news_sources = {
        "de": {
            "rss": [
                "https://www.spiegel.de/schlagzeilen/index.rss",
                "https://www.electrive.net/feed/",
                "https://www.automobil-industrie.vogel.de/rss/news.xml",
                "https://www.handelsblatt.com/auto/rss",
                "https://www.wiwo.de/rss/auto",
                "https://www.stern.de/auto/feed.rss"
            ]
        }
    }
    
    # RSS настройки
    rss_settings = {
        'timeout': 10,
        'retry_count': 3,
        'min_sources': 2,
        'cache_time': 900
    }
    
    # Настройки публикации
    publish_times = ["09:00", "11:00", "15:00", "17:00"]
    posts_per_time = 2
    
    # Настройки логирования
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'file': {
                'level': 'INFO',
                'class': 'logging.FileHandler',
                'filename': 'logs/newsbot.log',
            },
        },
        'loggers': {
            '': {
                'handlers': ['file'],
                'level': 'INFO',
                'propagate': True,
            },
        },
    }
    
    try:
        config = Config(
            TELEGRAM_TOKEN=telegram_token,
            CHANNEL_ID=channel_id,
            ADMIN_ID=admin_id,
            DATABASE_URL=database_url,
            NEWS_SOURCES=news_sources,
            RSS_SETTINGS=rss_settings,
            PUBLISH_TIMES=publish_times,
            POSTS_PER_TIME=posts_per_time,
            LOGGING_CONFIG=logging_config
        )
        logger.info("Configuration loaded successfully")
        return config
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        raise

# Создаем глобальный экземпляр конфигурации
config = None
try:
    config = load_config()
except Exception as e:
    logger.error(f"Failed to load configuration: {e}")
    raise

# Экспортируем только необходимые компоненты
__all__ = ['load_config', 'config', 'Config']

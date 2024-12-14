import os
from typing import Dict, List

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
CHANNEL_ID = os.environ.get('CHANNEL_ID', '')

# RSS Source Configurations
NEWS_SOURCES = {
    "de": {
        "rss": [
            # Основные автомобильные издания
            "https://www.electrive.net/feed/",
            "https://www.automobil-industrie.vogel.de/rss/news.xml",
            "https://www.auto-motor-und-sport.de/feed/",
            "https://www.autozeitung.de/feed",
            
            # Специализированные EV источники
            "https://ecomento.de/feed/",
            "https://www.elektroauto-news.net/feed",
            "https://www.goingelectric.de/feed/",
            
            # Экономические издания
            "https://www.handelsblatt.com/auto/rss",
            "https://www.wiwo.de/rss/auto",
            
            # Технологические издания
            "https://www.heise.de/autos/rss/news.rdf",
            "https://www.elektroniknet.de/rss/emobility.xml",
            
            # Общие новостные источники
            "https://www.spiegel.de/auto/rss.xml",
            "https://www.stern.de/auto/feed.rss",
            "https://www.focus.de/auto/rss.xml",
            
            # Отраслевые издания
            "https://www.automotive-it.info/rss.xml",
            "https://www.emobilitaetblog.de/feed/"
        ]
    }
}

# Категории и ключевые слова
CATEGORIES_KEYWORDS = {
    'News': [
        'Elektroautos', 'EV', 'E-Auto', 'Elektromobilitaet',
        'Elektrofahrzeug', 'Stromer', 'E-Mobil', 'Elektro-SUV',
        'Elektrolimousine', 'E-Modell', 'Elektrovariante',
        'Elektrifizierung', 'elektrisch angetrieben'
    ],
    'Wirtschaft': [
        'EV-Markt', 'Verkaufszahlen', 'Absatz', 'Umsatz',
        'Investition', 'Förderung', 'Subvention', 'Kaufprämie',
        'Umweltbonus', 'Marktanteil', 'Produktionsstart',
        'Verkaufsstart', 'Auslieferung', 'Batterieproduktion',
        'Preise', 'Kosten', 'Gewinn', 'Verlust'
    ],
    'Sport': [
        'Formel E', 'Rennsport', 'Motorsport', 'Rekord',
        'Beschleunigung', 'Rundenzeit', 'Rennstrecke',
        'Performance', 'Höchstgeschwindigkeit', 'Sprint'
    ],
    'Technologie': [
        'Batterie', 'Akku', 'Reichweite', 'Laden', 'kWh',
        'Ladezeit', 'Schnellladen', 'Ladeleistung', 'Volt',
        'Ampere', 'Energiedichte', 'Zelltechnologie',
        'Ladesäule', 'Ladestation', 'Ladepunkt', 'Wallbox',
        'Antrieb', 'Motor', 'Software', 'Update'
    ],
    'Trends': [
        'Hybrid', 'Wasserstoff', 'Brennstoffzelle', 'Solar',
        'Vehicle-to-Grid', 'Sharing', 'Carsharing', 'Mobility',
        'Vernetzung', 'Connectivity', 'Smart', 'Digital',
        'Zukunft', 'Innovation', 'Studie', 'Concept'
    ],
    'Transport': [
        'LKW', 'Transporter', 'Nutzfahrzeug', 'Bus',
        'Lieferwagen', 'Logistik', 'Transport', 'Fleet',
        'Flotte', 'Taxi', 'ÖPNV', 'Nahverkehr', 'Shuttle'
    ]
}

# RSS Feed Settings
RSS_SETTINGS = {
    'timeout': 15,              # Таймаут запросов в секундах
    'retry_count': 3,          # Количество попыток при ошибке
    'min_sources': 2,          # Минимум активных источников
    'cache_time': 900,         # Время кэширования (15 минут)
    'user_agent': 'Mozilla/5.0 (compatible; NewsBot/1.0; +http://example.com)',
    'source_weights': {        # Приоритеты источников
        'electrive.net': 1.0,
        'automobil-industrie.vogel.de': 0.9,
        'ecomento.de': 0.9,
        'goingelectric.de': 0.9,
        'heise.de': 0.8,
        'spiegel.de': 0.8
    },
    'default_weight': 0.7      # Вес по умолчанию для остальных источников
}

# Настройки публикации
PUBLISH_SETTINGS = {
    'times': ["09:00", "11:00", "15:00", "17:00"],  # Время публикаций
    'posts_per_time': 2,                            # Количество постов
    'min_interval': 3600,                           # Минимальный интервал (1 час)
    'max_posts_per_day': 8                          # Максимум постов в день
}

# Logging Configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/newsbot.log',
            'formatter': 'standard'
        },
    },
    'loggers': {
        '': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True
        },
    }
}

def classify_by_keywords(title: str) -> str:
    """
    Классификация новости по заголовку
    
    Args:
        title (str): Заголовок новости
        
    Returns:
        str: Категория новости
    """
    title_lower = title.lower()
    matches = {
        category: sum(1 for keyword in keywords 
                     if keyword.lower() in title_lower)
        for category, keywords in CATEGORIES_KEYWORDS.items()
    }
    
    if any(matches.values()):
        return max(matches.items(), key=lambda x: x[1])[0]
    return 'News'  # Категория по умолчанию

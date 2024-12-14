import json
import os
from utils.logger import get_logger

logger = get_logger()

class TopicManager:
    def __init__(self):
        self.config_file = 'config/topics.json'
        self.load_config()
    
    def load_config(self):
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.topics = json.load(f)
        except FileNotFoundError:
            # Если файл не найден, создаем конфигурацию по умолчанию
            self.topics = {
                'main_topic': 'E-Auto',
                'categories': {
                    'News': [
                        'Elektroautos', 'EV', 'E-Auto', 'Elektromobilität',
                        'Elektrofahrzeug', 'Stromer', 'E-Mobilität', 'Ladestrom'
                    ],
                    'Wirtschaft': [
                        'Tesla', 'Volkswagen', 'BMW', 'Mercedes', 'Porsche',
                        'Batterie', 'Elektromarkt', 'BYD', 'NIO'
                    ],
                    'Sport': [
                        'Formel E', 'E-Motorsport', 'Tesla Plaid', 
                        'Rimac', 'Elektro-Rennsport'
                    ],
                    'Technologie': [
                        'Batterie', 'Laden', 'Reichweite', 'Akku',
                        'Elektroantrieb', 'Ladesäule', 'kWh'
                    ],
                    'Trends': [
                        'Hybrid', 'Wasserstoff', 'Solar', 'Elektro',
                        'Plug-in', 'PHEV', 'BEV'
                    ],
                    'Transport': [
                        'E-Bus', 'E-Lkw', 'Elektro-Transport',
                        'E-Lieferfahrzeug', 'E-Transporter'
                    ]
                }
            }
            # Создаем директорию, если её нет
            os.makedirs('config', exist_ok=True)
            self.save_config()
            logger.info("Created default topic configuration")
    
    def save_config(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.topics, f, indent=4, ensure_ascii=False)
            logger.info("Saved topic configuration")
        except Exception as e:
            logger.error(f"Error saving topic configuration: {e}")
    
    def update_topics(self, new_topics):
        """Обновляет конфигурацию тем и ключевых слов"""
        self.topics = new_topics
        self.save_config()

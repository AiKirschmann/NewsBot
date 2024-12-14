from transformers import pipeline
from utils.logger import get_logger
from utils.topic_manager import TopicManager
import re

logger = get_logger()

class NewsAnalyzer:
    def __init__(self):
        try:
            self.classifier = pipeline(
                "sentiment-analysis",
                model="nlptown/bert-base-multilingual-uncased-sentiment",
                max_length=512
            )
            self.topic_manager = TopicManager()
            logger.info("NewsAnalyzer initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing NewsAnalyzer: {e}")
            raise

    def is_relevant_news(self, title, description=""):
        """Проверяет соответствие новости тематике"""
        text = (title + " " + description).lower()
        main_topic = self.topic_manager.topics['main_topic'].lower()
        
        # Проверяем основную тему
        if main_topic not in text:
            return False
            
        # Проверяем ключевые слова по категориям
        for category, keywords in self.topic_manager.topics['categories'].items():
            if any(keyword.lower() in text for keyword in keywords):
                return True
        
        return False

    def classify_news(self, title, description=""):
        """Определяет категорию новости"""
        text = (title + " " + description).lower()
        
        for category, keywords in self.topic_manager.topics['categories'].items():
            if any(keyword.lower() in text for keyword in keywords):
                return category
        
        return 'Allgemein'

    def analyze_news(self, news_items):
        analyzed_news = []
        try:
            for item in news_items:
                # Проверяем релевантность
                if not self.is_relevant_news(item['title']):
                    continue
                
                # Определяем категорию
                item['category'] = self.classify_news(item['title'])
                
                # Анализ тональности
                sentiment = self.classifier(item['title'])[0]
                item['sentiment_score'] = float(sentiment['label'].split()[0]) / 5.0
                
                # Добавляем время чтения
                words = len(item['title'].split())
                item['read_time'] = f"{max(1, round(words/20))} min"
                
                analyzed_news.append(item)
                logger.info(f"Analyzed: {item['title'][:50]}... | Category: {item['category']}")
            
            # Сортируем по релевантности
            analyzed_news.sort(key=lambda x: x['sentiment_score'], reverse=True)
            return analyzed_news
            
        except Exception as e:
            logger.error(f"Error in news analysis: {e}")
            return []

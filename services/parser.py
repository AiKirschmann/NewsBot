import feedparser
from datetime import datetime
from utils.logger import get_logger
from utils.config import NEWS_SOURCES

logger = get_logger()

class NewsParser:
    def __init__(self):
        self.sources = NEWS_SOURCES
    
    def parse_news(self, language='en'):
        news_items = []
        for rss_url in self.sources[language]['rss']:
            try:
                feed = feedparser.parse(rss_url)
                for entry in feed.entries:
                    news_items.append({
                        'title': entry.title,
                        'link': entry.link,
                        'pub_date': datetime.now(),
                        'language': language
                    })
                logger.info(f"Successfully parsed {rss_url}")
            except Exception as e:
                logger.error(f"Error parsing {rss_url}: {e}")
        return news_items

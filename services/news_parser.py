import requests
import logging
import xml.etree.ElementTree as ET
from config.settings import NEWS_SOURCES

class NewsParser:
    def __init__(self, config=NEWS_SOURCES):
        self.sources = config
        logging.basicConfig(**LOGGING_CONFIG)
        self.logger = logging.getLogger(__name__)

    def fetch_rss(self, url):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return ET.fromstring(response.content)
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return None

    def parse_feed(self, url):
        feed = self.fetch_rss(url)
        if feed is None:
            return []

        news_items = []
        for item in feed.findall(".//item"):
            try:
                title = item.find("title").text
                link = item.find("link").text
                news_items.append({"title": title, "link": link})
            except Exception as e:
                self.logger.warning(f"Error parsing item: {e}")
        
        return news_items

    def get_news_by_language(self, lang):
        all_news = []
        for url in self.sources.get(lang, {}).get("aggregators", []) + \
                   self.sources.get(lang, {}).get("specialized", []):
            all_news.extend(self.parse_feed(url))
        return all_news

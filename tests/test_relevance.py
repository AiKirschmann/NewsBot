import asyncio
from services.analyzer import NewsAnalyzer
from utils.config import NEWS_SOURCES
import feedparser

async def test_relevance():
    analyzer = NewsAnalyzer()
    
    print("\n🔍 Проверка релевантности новостей")
    print("================================")
    
    total_relevant = 0
    
    for source in NEWS_SOURCES['de']['rss']:
        try:
            feed = feedparser.parse(source)
            if not hasattr(feed, 'entries'):
                continue
                
            print(f"\n📰 Источник: {source}")
            relevant_count = 0
            
            for entry in feed.entries:
                if analyzer.is_relevant_news(entry.title):
                    relevant_count += 1
                    total_relevant += 1
                    print(f"✅ {entry.title}")
            
            print(f"Найдено релевантных новостей: {relevant_count}")
            
        except Exception as e:
            print(f"❌ Ошибка при проверке {source}: {e}")
    
    print(f"\n📊 Итого релевантных новостей: {total_relevant}")

if __name__ == "__main__":
    asyncio.run(test_relevance())

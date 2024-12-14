import asyncio
import feedparser
import time
from datetime import datetime
from utils.config import NEWS_SOURCES  # Добавляем импорт

async def test_all_sources():
    sources = NEWS_SOURCES["de"]["rss"]
    
    print(f"Тестирование {len(sources)} источников\n")
    working_sources = []
    
    for source in sources:
        try:
            print(f"Проверка: {source}")
            feed = feedparser.parse(source)
            
            if hasattr(feed, 'status') and feed.status == 200:
                entries_count = len(feed.entries)
                print(f"✅ Работает. Найдено записей: {entries_count}")
                if entries_count > 0:
                    print("Последние записи:")
                    for entry in feed.entries[:2]:
                        print(f"- {entry.title}")
                        print(f"  Дата: {entry.get('published', 'Нет даты')}\n")
                working_sources.append(source)
            else:
                print("❌ Ошибка доступа\n")
                
            # Пауза между запросами
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"❌ Ошибка: {str(e)}\n")
    
    print("\nИтоги:")
    print(f"Всего источников: {len(sources)}")
    print(f"Работает: {len(working_sources)}")
    
    if working_sources:
        print("\nРаботающие источники:")
        for source in working_sources:
            print(f"- {source}")

if __name__ == "__main__":
    asyncio.run(test_all_sources())

from services.parser import NewsParser
from services.analyzer import NewsAnalyzer
import asyncio

async def test():
    parser = NewsParser()
    analyzer = NewsAnalyzer()
    
    # Получаем новости
    print("\n📰 Тестирование парсера и анализатора")
    print("=====================================")
    
    news = parser.parse_news(language='de')
    print(f"\nНайдено новостей: {len(news)}")
    
    # Показываем первые 5 новостей до анализа
    print("\nПримеры новостей до анализа:")
    for i, item in enumerate(news[:5]):
        print(f"{i+1}. {item['title']}")
    
    # Анализируем
    analyzed = analyzer.analyze_news(news)
    print(f"\nОтфильтровано релевантных: {len(analyzed)}")
    
    if analyzed:
        print("\nРелевантные новости:")
        for i, item in enumerate(analyzed):
            print(f"{i+1}. [{item['category']}] {item['title']}")
    else:
        print("\nРелевантных новостей не найдено. Проверяем ключевые слова...")
        print("\nТекущие ключевые слова:")
        from utils.topic_manager import TopicManager
        tm = TopicManager()
        for category, keywords in tm.topics['categories'].items():
            print(f"\n{category}:")
            print(", ".join(keywords))

if __name__ == "__main__":
    asyncio.run(test())

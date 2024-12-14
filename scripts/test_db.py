import os
from dotenv import load_dotenv
import psycopg2
from utils.logger import get_logger

logger = get_logger()

load_dotenv()

def test_database():
    try:
        # Подключаемся к базе данных
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
        
        # Создаем тестовую таблицу
        cur.execute("""
            CREATE TABLE IF NOT EXISTS news (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                link TEXT NOT NULL,
                category TEXT,
                sentiment_score FLOAT,
                published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Создаем таблицу статистики
        cur.execute("""
            CREATE TABLE IF NOT EXISTS stats (
                id SERIAL PRIMARY KEY,
                date DATE DEFAULT CURRENT_DATE,
                category TEXT,
                news_count INTEGER,
                avg_sentiment_score FLOAT
            )
        """)
        
        conn.commit()
        print("✅ Database tables created successfully!")
        
        # Проверяем, что таблицы созданы
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = cur.fetchall()
        print("\nExisting tables:")
        for table in tables:
            print(f"📋 {table[0]}")
            
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Database test error: {e}")

if __name__ == "__main__":
    print("Testing database connection and setup...")
    test_database()

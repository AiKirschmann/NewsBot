import psycopg2
from contextlib import contextmanager
from utils.logger import setup_logger
from utils.config import config

logger = setup_logger(__name__)

class DatabaseManager:
    def __init__(self):
        self.database_url = config.DATABASE_URL
        self.conn = None
        self._setup_connection()

    def _setup_connection(self):
        """Настройка подключения к базе данных"""
        try:
            self.conn = psycopg2.connect(self.database_url)
            logger.info("Database connection initialized successfully")
        except Exception as e:
            logger.error(f"Failed to setup database connection: {e}")
            raise

    @contextmanager
    def get_db_session(self):
        """Контекстный менеджер для подключения"""
        conn = None
        try:
            conn = psycopg2.connect(self.database_url)
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def init_database(self):
        """Инициализация базы данных"""
        try:
            with self.get_db_session() as conn:
                with conn.cursor() as cur:
                    # Создаем таблицу новостей
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS news (
                            id SERIAL PRIMARY KEY,
                            title VARCHAR(500) NOT NULL,
                            link VARCHAR(500) UNIQUE NOT NULL,
                            content TEXT,
                            category VARCHAR(50) NOT NULL,
                            sentiment_score FLOAT DEFAULT 0.0,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                            published_at TIMESTAMP WITH TIME ZONE
                        )
                    """)

                    # Создаем таблицу публикаций
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS publications (
                            id SERIAL PRIMARY KEY,
                            news_id INTEGER REFERENCES news(id) NOT NULL,
                            channel_id VARCHAR(100) NOT NULL,
                            message_id INTEGER,
                            status VARCHAR(20) DEFAULT 'pending',
                            scheduled_time TIMESTAMP WITH TIME ZONE NOT NULL,
                            published_at TIMESTAMP WITH TIME ZONE,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                        )
                    """)

                    # Создаем таблицу статистики
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS stats (
                            id SERIAL PRIMARY KEY,
                            date TIMESTAMP WITH TIME ZONE NOT NULL,
                            category VARCHAR(50) NOT NULL,
                            news_count INTEGER DEFAULT 0,
                            avg_sentiment_score FLOAT DEFAULT 0.0,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE(date, category)
                        )
                    """)

                    # Создаем индексы
                    cur.execute("CREATE INDEX IF NOT EXISTS idx_news_link ON news(link)")
                    cur.execute("CREATE INDEX IF NOT EXISTS idx_news_category ON news(category)")
                    cur.execute("CREATE INDEX IF NOT EXISTS idx_news_created_at ON news(created_at)")
                    
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def save_news(self, news_item):
        """Сохранение новости в базу данных"""
        try:
            with self.get_db_session() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO news (title, link, category, sentiment_score)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (link) DO NOTHING
                        RETURNING id
                    """, (
                        news_item['title'],
                        news_item['link'],
                        news_item['category'],
                        news_item.get('sentiment_score', 0)
                    ))
                    result = cur.fetchone()
                    return result[0] if result else None
        except Exception as e:
            logger.error(f"Error saving news: {e}")
            return None

    def is_published(self, link):
        """Проверка, была ли новость уже опубликована"""
        try:
            with self.get_db_session() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT id FROM news WHERE link = %s", (link,))
                    return cur.fetchone() is not None
        except Exception as e:
            logger.error(f"Error checking published news: {e}")
            return False

    def update_stats(self):
        """Обновление статистики"""
        try:
            with self.get_db_session() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO stats (date, category, news_count, avg_sentiment_score)
                        SELECT
                            CURRENT_DATE,
                            category,
                            COUNT(*),
                            AVG(sentiment_score)
                        FROM news
                        WHERE DATE(created_at) = CURRENT_DATE
                        GROUP BY category
                        ON CONFLICT (date, category) 
                        DO UPDATE SET
                            news_count = EXCLUDED.news_count,
                            avg_sentiment_score = EXCLUDED.avg_sentiment_score
                    """)
            logger.info("Statistics updated successfully")
        except Exception as e:
            logger.error(f"Error updating stats: {e}")

    def get_daily_stats(self):
        """Получение статистики за текущий день"""
        try:
            with self.get_db_session() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT category, news_count, avg_sentiment_score
                        FROM stats
                        WHERE date = CURRENT_DATE
                    """)
                    return cur.fetchall()
        except Exception as e:
            logger.error(f"Error getting daily stats: {e}")
            return []

# Создаем глобальный экземпляр менеджера базы данных
db_manager = DatabaseManager()

# Экспортируем функции для использования в других модулях
get_db_session = db_manager.get_db_session

__all__ = ['db_manager', 'get_db_session']

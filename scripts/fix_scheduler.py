#!/usr/bin/env python3

import asyncio
from datetime import datetime, timedelta
from database.connection import get_db_session
from utils.config import config
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Ключевые слова для фильтрации E-Auto новостей
EV_KEYWORDS = [
    'elektro', 'e-auto', 'ev', 'batterie', 'laden', 'tesla', 
    'volkswagen', 'bmw', 'elektroauto', 'elektromobil', 'stromer',
    'reichweite', 'ladestation', 'elektroantrieb', 'emobility',
    'elektrifizierung', 'akku'
]

async def fix_publications():
    try:
        with get_db_session() as conn:
            with conn.cursor() as cur:
                # Очистка существующих публикаций
                cur.execute("DELETE FROM publications WHERE status = 'pending'")
                
                # Создаем временную таблицу для фильтрации по ключевым словам
                cur.execute("""
                    CREATE TEMP TABLE relevant_news AS
                    SELECT id, title, category, created_at,
                           CASE 
                               WHEN category = 'News' THEN 1
                               WHEN category = 'Wirtschaft' THEN 2
                               ELSE 3
                           END as priority
                    FROM news 
                    WHERE created_at >= CURRENT_DATE - INTERVAL '2 days'
                    AND (
                        """ + " OR ".join([f"LOWER(title) LIKE '%{kw}%'" for kw in EV_KEYWORDS]) + """
                        OR category IN ('News', 'Wirtschaft')
                    )
                    ORDER BY priority, created_at DESC;
                """)

                # Получаем отфильтрованные новости
                cur.execute("SELECT COUNT(*) FROM relevant_news")
                total_news = cur.fetchone()[0]
                logger.info(f"Found {total_news} relevant news")

                now = datetime.now()
                today = now.date()
                tomorrow = today + timedelta(days=1)

                for day in [today, tomorrow]:
                    for time_str in config.PUBLISH_TIMES:
                        hour, minute = map(int, time_str.split(':'))
                        pub_time = datetime.combine(
                            day, 
                            datetime.min.time().replace(hour=hour, minute=minute)
                        )
                        
                        if pub_time <= now:
                            continue

                        # Планируем ровно 2 публикации на каждый слот
                        cur.execute("""
                            INSERT INTO publications (news_id, channel_id, scheduled_time, status)
                            SELECT id, %s, %s, 'pending'
                            FROM (
                                SELECT id 
                                FROM relevant_news
                                WHERE id NOT IN (
                                    SELECT news_id FROM publications
                                    WHERE status = 'pending'
                                )
                                ORDER BY priority, created_at DESC
                                LIMIT 2
                            ) selected_news
                        """, (config.CHANNEL_ID, pub_time))

                        # Логируем запланированные публикации
                        cur.execute("""
                            SELECT n.title, n.category
                            FROM publications p
                            JOIN news n ON p.news_id = n.id
                            WHERE p.scheduled_time = %s
                        """, (pub_time,))
                        
                        planned = cur.fetchall()
                        logger.info(f"\nScheduled for {pub_time}:")
                        for title, category in planned:
                            logger.info(f"- [{category}] {title}")

                # Очистка временной таблицы
                cur.execute("DROP TABLE IF EXISTS relevant_news")
                conn.commit()
                
                logger.info("Publications scheduling completed successfully")

    except Exception as e:
        logger.error(f"Error fixing publications: {e}")
        if 'conn' in locals():
            conn.rollback()

if __name__ == "__main__":
    asyncio.run(fix_publications())

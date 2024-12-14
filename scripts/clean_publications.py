#!/usr/bin/env python3

import asyncio
from datetime import datetime, timedelta
from database.connection import get_db_session
from utils.config import config
from utils.logger import setup_logger

logger = setup_logger(__name__)

EV_KEYWORDS = [
    'elektro', 'e-auto', 'ev', 'batterie', 'laden', 'tesla', 
    'ladestrom', 'habeck', 'enyaq', 'inverter'
]

async def clean_and_schedule():
    try:
        with get_db_session() as conn:
            with conn.cursor() as cur:
                # 1. Очистка старых публикаций
                cur.execute("DELETE FROM publications WHERE status = 'pending'")
                
                # 2. Выбор релевантных новостей
                news_filter = " OR ".join([f"LOWER(title) LIKE '%{kw}%'" for kw in EV_KEYWORDS])
                query = f"""
                    SELECT id, title, category, created_at
                    FROM news 
                    WHERE ({news_filter})
                    AND created_at >= CURRENT_TIMESTAMP - interval '2 days'
                    ORDER BY created_at DESC;
                """
                
                cur.execute(query)
                news = cur.fetchall()
                
                if not news:
                    logger.info("No relevant news found")
                    return
                
                logger.info(f"Found {len(news)} E-Auto news")
                
                # 3. Планирование по 2 новости на слот
                now = datetime.now()
                today = now.date()
                tomorrow = today + timedelta(days=1)
                news_index = 0
                
                for day in [today, tomorrow]:
                    for time_str in config.PUBLISH_TIMES:
                        if news_index >= len(news):
                            break
                            
                        hour, minute = map(int, time_str.split(':'))
                        pub_time = datetime.combine(day, datetime.min.time().replace(hour=hour, minute=minute))
                        
                        if pub_time <= now:
                            continue
                        
                        # Планируем 2 новости
                        for _ in range(2):
                            if news_index >= len(news):
                                break
                                
                            news_id, title, category, created = news[news_index]
                            cur.execute("""
                                INSERT INTO publications 
                                (news_id, channel_id, scheduled_time, status)
                                VALUES (%s, %s, %s, 'pending')
                            """, (news_id, config.CHANNEL_ID, pub_time))
                            
                            logger.info(f"Scheduled for {pub_time}: {title}")
                            news_index += 1
                
                conn.commit()
                logger.info("Publications scheduled successfully")

    except Exception as e:
        logger.error(f"Error in scheduling: {e}")
        if 'conn' in locals():
            conn.rollback()

if __name__ == "__main__":
    asyncio.run(clean_and_schedule())

import asyncio
from datetime import datetime, timedelta
from utils.logger import setup_logger
from utils.config import config
from database.connection import get_db_session

logger = setup_logger(__name__)

class NewsScheduler:
    def __init__(self):
        self.is_running = False
        self.task = None

    async def initialize(self):
        try:
            await self._schedule_next_publications()
            logger.info("Scheduler initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize scheduler: {e}")
            return False

    async def start(self):
        self.is_running = True
        self.task = asyncio.create_task(self._run())
        logger.info("Scheduler started successfully")

    async def stop(self):
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Scheduler stopped successfully")

    async def _run(self):
        while self.is_running:
            try:
                await self._schedule_next_publications()
                await asyncio.sleep(60)
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(60)

    async def _schedule_next_publications(self):
        try:
            now = datetime.now()
            today = now.date()
            tomorrow = today + timedelta(days=1)

            with get_db_session() as conn:
                with conn.cursor() as cur:
                    # Очищаем старые публикации
                    cur.execute("""
                        DELETE FROM publications
                        WHERE status = 'pending'
                        AND scheduled_time < CURRENT_TIMESTAMP
                    """)

                    # Планируем на каждый таймслот
                    for day in [today, tomorrow]:
                        for time_str in config.PUBLISH_TIMES:
                            hour, minute = map(int, time_str.split(':'))
                            pub_time = datetime.combine(
                                day,
                                datetime.min.time().replace(hour=hour, minute=minute)
                            )

                            if pub_time <= now:
                                continue

                            # Выбираем только 2 новости для каждого слота
                            cur.execute("""
                                WITH available_news AS (
                                    SELECT 
                                        n.id,
                                        n.title,
                                        n.category,
                                        n.created_at
                                    FROM news n
                                    WHERE NOT EXISTS (
                                        SELECT 1 FROM publications p
                                        WHERE p.news_id = n.id
                                        AND (p.status = 'published' OR p.status = 'pending')
                                    )
                                    ORDER BY 
                                        CASE 
                                            WHEN n.category = 'News' THEN 1
                                            WHEN n.category = 'Wirtschaft' THEN 2
                                            ELSE 3
                                        END,
                                        n.created_at DESC
                                )
                                INSERT INTO publications (news_id, channel_id, scheduled_time, status)
                                SELECT 
                                    id,
                                    %s,
                                    %s,
                                    'pending'
                                FROM available_news
                                LIMIT %s
                            """, (config.CHANNEL_ID, pub_time, config.POSTS_PER_TIME))

                            # Логируем результат
                            planned = cur.rowcount
                            logger.info(f"Scheduled {planned} posts for {pub_time}")

                    conn.commit()

                    # Проверяем итоговое расписание
                    cur.execute("""
                        SELECT n.title, n.category, p.scheduled_time
                        FROM publications p
                        JOIN news n ON p.news_id = n.id
                        WHERE p.status = 'pending'
                        ORDER BY p.scheduled_time
                    """)
                    schedule = cur.fetchall()
                    logger.info(f"Total scheduled publications: {len(schedule)}")
                    for title, category, time in schedule:
                        logger.info(f"Scheduled: {time} - [{category}] {title}")

        except Exception as e:
            logger.error(f"Error scheduling publications: {e}")
            if 'conn' in locals():
                conn.rollback()

    def get_status(self) -> dict:
        return {
            'is_running': self.is_running,
            'task_active': self.task is not None and not self.task.done()
        }

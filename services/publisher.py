from datetime import datetime, timedelta
from aiogram import Bot
from utils.logger import setup_logger
from database.connection import db_manager
from utils.config import config

logger = setup_logger(__name__)

class NewsPublisher:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.channel_id = config.CHANNEL_ID

    async def publish_news(self, news_item):
        """Публикация новости в канал"""
        try:
            # Форматируем сообщение
            message = self._format_news(news_item)
            
            # Отправляем в Telegram
            result = await self.bot.send_message(
                chat_id=self.channel_id,
                text=message,
                parse_mode='HTML',
                disable_web_page_preview=False
            )
            
            # Обновляем статус в базе данных
            with db_manager.get_db_session() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE publications 
                        SET status = 'published', 
                            published_at = CURRENT_TIMESTAMP,
                            message_id = %s 
                        WHERE news_id = %s
                    """, (result.message_id, news_item['id']))
            
            logger.info(f"News published successfully: {news_item['title'][:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error publishing news: {e}")
            with db_manager.get_db_session() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE publications 
                        SET status = 'failed'
                        WHERE news_id = %s
                    """, (news_item['id'],))
            return False

    def _format_news(self, news):
        """Форматирование новости для публикации"""
        return (
            f"<b>{news['title']}</b>\n\n"
            f"{news.get('content', '')}\n\n"
            f"<a href='{news['link']}'>Подробнее...</a>\n\n"
            f"#EV #{news['category']}"
        )

    async def get_next_post(self):
        """Получение следующей запланированной публикации"""
        try:
            with db_manager.get_db_session() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT n.*, p.scheduled_time 
                        FROM publications p
                        JOIN news n ON p.news_id = n.id
                        WHERE p.status = 'pending'
                        AND p.scheduled_time > CURRENT_TIMESTAMP
                        ORDER BY p.scheduled_time
                        LIMIT 1
                    """)
                    result = cur.fetchone()
                    
                    if result:
                        return {
                            'id': result[0],
                            'title': result[5],
                            'link': result[6],
                            'category': result[4],
                            'scheduled_time': result[-1].strftime('%Y-%m-%d %H:%M:%S')
                        }
            return None
        except Exception as e:
            logger.error(f"Error getting next post: {e}")
            return None

    async def get_schedule(self):
        """Получение расписания публикаций"""
        try:
            with db_manager.get_db_session() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT n.title, p.scheduled_time, p.status
                        FROM publications p
                        JOIN news n ON p.news_id = n.id
                        WHERE p.scheduled_time > CURRENT_TIMESTAMP
                        ORDER BY p.scheduled_time
                        LIMIT 10
                    """)
                    results = cur.fetchall()
                    
                    return [{
                        'title': row[0],
                        'scheduled_time': row[1].strftime('%Y-%m-%d %H:%M:%S'),
                        'status': row[2]
                    } for row in results]
        except Exception as e:
            logger.error(f"Error getting schedule: {e}")
            return []

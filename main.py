import asyncio
import sys
import signal
from utils.logger import setup_logger
from utils.config import config
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from services.scheduler import NewsScheduler
from aiogram.filters import Command
import logging
from datetime import datetime
from database.connection import get_db_session  # Добавлен импорт

# Настройка логирования
logger = setup_logger(__name__)
logging.basicConfig(level=logging.INFO)

# Глобальные переменные для бота и диспетчера
bot = None
dp = None
scheduler = None
start_time = None

async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    try:
        if str(message.from_user.id) == config.ADMIN_ID:
            await message.reply(
                "👋 Добро пожаловать в панель администратора!\n\n"
                "Доступные команды:\n"
                "/help - Показать список команд\n"
                "/stats - Показать статистику\n"
                "/status - Проверить статус бота\n"
                "/next - Показать следующий пост\n"
                "/schedule - Показать расписание публикаций"
            )
        else:
            await message.reply("Извините, у вас нет прав администратора.")
    except Exception as e:
        logger.error(f"Error in start command: {e}")

async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    try:
        if str(message.from_user.id) == config.ADMIN_ID:
            help_text = """
📚 Список доступных команд:

Основные команды:
/start - Начать работу с ботом
/help - Показать это сообщение
/status - Проверить статус бота

Статистика и мониторинг:
/stats - Показать общую статистику
/schedule - Показать расписание публикаций
/next - Информация о следующем посте

Управление постами:
/skip - Пропустить следующий пост
/force - Принудительно опубликовать пост
/pause - Приостановить публикации
/resume - Возобновить публикации
"""
            await message.reply(help_text)
    except Exception as e:
        logger.error(f"Error in help command: {e}")

async def cmd_status(message: types.Message):
    """Обработчик команды /status"""
    try:
        if str(message.from_user.id) == config.ADMIN_ID:
            uptime = datetime.now() - start_time
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            status = "🤖 Статус бота:\n\n"
            status += f"✅ Бот активен\n"
            status += f"⏱ Время работы: {days}д {hours}ч {minutes}м {seconds}с\n"
            status += f"🔄 Планировщик: {'Работает' if scheduler and scheduler.is_running else 'Остановлен'}"
            
            await message.reply(status)
    except Exception as e:
        logger.error(f"Error in status command: {e}")

async def cmd_stats(message: types.Message):
    """Обработчик команды /stats"""
    try:
        if str(message.from_user.id) == config.ADMIN_ID:
            uptime = datetime.now() - start_time
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            stats = "📊 Статистика системы:\n\n"
            stats += f"⏱ Время работы: {days}д {hours}ч {minutes}м {seconds}с\n"
            stats += f"✅ Статус планировщика: {'Работает' if scheduler and scheduler.is_running else 'Остановлен'}\n"
            
            try:
                with get_db_session() as conn:
                    with conn.cursor() as cur:
                        # Общее количество новостей
                        cur.execute("SELECT COUNT(*) FROM news")
                        total_news = cur.fetchone()
                        total_news = total_news[0] if total_news else 0
                        
                        # Опубликованные новости (проверяем published_at)
                        cur.execute("""
                            SELECT COUNT(*) FROM news 
                            WHERE published_at IS NOT NULL 
                            AND published_at <= CURRENT_TIMESTAMP
                        """)
                        published_news = cur.fetchone()
                        published_news = published_news[0] if published_news else 0
                        
                        # Статистика по категориям
                        cur.execute("""
                            SELECT 
                                COALESCE(category, 'Без категории') as cat, 
                                COUNT(*),
                                COUNT(*) FILTER (WHERE published_at IS NOT NULL) as published
                            FROM news 
                            GROUP BY cat 
                            ORDER BY COUNT(*) DESC
                        """)
                        categories = cur.fetchall()
                        
                        # Следующая публикация
                        cur.execute("""
                            SELECT n.title, p.scheduled_time
                            FROM publications p
                            JOIN news n ON p.news_id = n.id
                            WHERE p.status = 'pending'
                            AND p.scheduled_time > CURRENT_TIMESTAMP
                            ORDER BY p.scheduled_time
                            LIMIT 1
                        """)
                        next_pub = cur.fetchone()

                stats += f"\n📰 Всего новостей: {total_news}\n"
                stats += f"📤 Опубликовано: {published_news}\n"
                
                if categories:
                    stats += "\n📋 По категориям:\n"
                    for cat, total, pub in categories:
                        stats += f"• {cat}: {total} (опубликовано: {pub})\n"
                
                if next_pub:
                    stats += f"\n⏰ Следующая публикация:\n"
                    stats += f"Заголовок: {next_pub[0][:50]}...\n"
                    stats += f"Время: {next_pub[1].strftime('%H:%M %d.%m.%Y')}"
                else:
                    # Определяем следующее время публикации
                    now = datetime.now()
                    current_time = now.strftime('%H:%M')
                    next_time = None
                    
                    for pub_time in config.PUBLISH_TIMES:
                        if pub_time > current_time:
                            next_time = pub_time
                            break
                    
                    if not next_time:
                        next_time = config.PUBLISH_TIMES[0]
                    
                    stats += f"\n⏰ Следующая публикация по расписанию: {next_time}"
            
            except Exception as db_error:
                logger.error(f"Database error in stats: {db_error}")
                stats += "\n⚠️ Ошибка при получении данных из базы"
            
            await message.reply(stats)
            
    except Exception as e:
        logger.error(f"Error in stats command: {e}")
        await message.reply("Ошибка при получении статистики. Попробуйте позже.")

async def cmd_schedule(message: types.Message):
    """Показать расписание публикаций"""
    try:
        if str(message.from_user.id) != config.ADMIN_ID:
            return

        with get_db_session() as conn:
            with conn.cursor() as cur:
                # Получаем запланированные публикации
                cur.execute("""
                    SELECT 
                        DATE(p.scheduled_time) as pub_date,
                        TO_CHAR(p.scheduled_time, 'HH24:MI') as pub_time,
                        COUNT(*) as posts_count,
                        string_agg(
                            CASE 
                                WHEN length(n.title) > 30 
                                THEN substring(n.title, 1, 30) || '...' 
                                ELSE n.title 
                            END, 
                            '\n'
                        ) as titles
                    FROM publications p
                    JOIN news n ON p.news_id = n.id
                    WHERE p.status = 'pending'
                    AND p.scheduled_time > CURRENT_TIMESTAMP
                    GROUP BY pub_date, pub_time
                    ORDER BY pub_date, pub_time
                """)
                schedule = cur.fetchall()

        response = "📅 Расписание публикаций:\n\n"

        if schedule:
            current_date = None
            for pub_date, pub_time, count, titles in schedule:
                if current_date != pub_date:
                    current_date = pub_date
                    response += f"\n📆 {pub_date.strftime('%d.%m.%Y')}:\n"
                response += f"⏰ {pub_time} ({count} публ.):\n"
                response += f"{titles}\n"
            
            response += f"\nВсего публикаций: {sum(count for _, _, count, _ in schedule)}"
        else:
            response += "🕒 Стандартное расписание:\n"
            for time in config.PUBLISH_TIMES:
                response += f"• {time}\n"
            response += "\nНет запланированных публикаций"
            response += "\nИспользуйте /plan для планирования"

        response += f"\n\nПостов за раз: {config.POSTS_PER_TIME}"
        
        await message.reply(response)
    except Exception as e:
        logger.error(f"Error in schedule command: {e}")
        await message.reply("Ошибка при получении расписания")

async def cmd_next(message: types.Message):
    """Показать следующие публикации"""
    try:
        if str(message.from_user.id) != config.ADMIN_ID:
            return

        with get_db_session() as conn:
            with conn.cursor() as cur:
                # Получаем следующие публикации с подробной информацией
                cur.execute("""
                    WITH upcoming AS (
                        SELECT 
                            n.title,
                            n.category,
                            p.scheduled_time,
                            n.created_at,
                            LAG(p.scheduled_time) OVER (ORDER BY p.scheduled_time) as prev_time
                        FROM publications p
                        JOIN news n ON p.news_id = n.id
                        WHERE p.status = 'pending'
                        AND p.scheduled_time > CURRENT_TIMESTAMP
                        ORDER BY p.scheduled_time
                        LIMIT 4
                    )
                    SELECT *,
                           CASE 
                               WHEN prev_time IS NULL OR DATE(scheduled_time) != DATE(prev_time)
                               THEN true 
                               ELSE false 
                           END as show_date
                    FROM upcoming
                """)
                next_posts = cur.fetchall()

        if not next_posts:
            now = datetime.now()
            current_time = now.strftime('%H:%M')
            next_time = None
            
            for time in config.PUBLISH_TIMES:
                if time > current_time:
                    next_time = time
                    break
                    
            if not next_time:
                next_time = config.PUBLISH_TIMES[0]
                
            response = "📭 Нет запланированных публикаций\n"
            response += f"\nСледующее время по расписанию: {next_time}\n"
            response += "\nИспользуйте /plan для планирования публикаций"
        else:
            response = "📬 Следующие публикации:\n"
            
            for title, category, scheduled_time, created_at, _, show_date in next_posts:
                if show_date:
                    response += f"\n📅 {scheduled_time.strftime('%d.%m.%Y')}:\n"
                    
                response += f"\n⏰ {scheduled_time.strftime('%H:%M')}\n"
                response += f"📰 {title}\n"
                response += f"📁 Категория: {category}\n"
                response += f"📅 Создано: {created_at.strftime('%d.%m.%Y %H:%M')}\n"

            response += "\nИспользуйте /schedule для полного расписания"

        await message.reply(response)
    except Exception as e:
        logger.error(f"Error in next command: {e}")
        await message.reply("Ошибка при получении информации о публикациях")

async def cmd_skip(message: types.Message):
    """Пропустить следующую публикацию"""
    try:
        if str(message.from_user.id) != config.ADMIN_ID:
            return

        with get_db_session() as conn:
            with conn.cursor() as cur:
                # Получаем следующую публикацию
                cur.execute("""
                    UPDATE publications
                    SET status = 'skipped'
                    WHERE id = (
                        SELECT id FROM publications
                        WHERE status = 'pending'
                        AND scheduled_time > CURRENT_TIMESTAMP
                        ORDER BY scheduled_time
                        LIMIT 1
                    )
                    RETURNING (
                        SELECT title FROM news WHERE id = news_id
                    );
                """)
                result = cur.fetchone()
                conn.commit()

        if result:
            await message.reply(f"✅ Публикация пропущена:\n{result[0]}")
        else:
            await message.reply("Нет запланированных публикаций для пропуска")

    except Exception as e:
        logger.error(f"Error in skip command: {e}")
        await message.reply("Ошибка при попытке пропустить публикацию")

async def cmd_plan(message: types.Message):
    """Команда планирования публикаций"""
    try:
        if str(message.from_user.id) != config.ADMIN_ID:
            return

        # Запускаем планирование
        await scheduler._schedule_next_publications()
        
        # Проверяем результат
        with get_db_session() as conn:
            with conn.cursor() as cur:
                # Проверяем запланированные публикации
                cur.execute("""
                    SELECT 
                        DATE(scheduled_time) as pub_date,
                        COUNT(*) as posts_count
                    FROM publications 
                    WHERE status = 'pending'
                    AND scheduled_time > CURRENT_TIMESTAMP
                    GROUP BY pub_date
                    ORDER BY pub_date
                """)
                schedule = cur.fetchall()

        response = "📋 Результаты планирования:\n\n"
        
        if schedule:
            total_posts = sum(count for _, count in schedule)
            response += f"✅ Всего запланировано: {total_posts} публикаций\n\n"
            for pub_date, count in schedule:
                response += f"📅 {pub_date.strftime('%d.%m.%Y')}: {count} публикаций\n"
            response += "\nИспользуйте /next для просмотра деталей"
        else:
            response += "⚠️ Нет доступных новостей для планирования"

        await message.reply(response)
        
    except Exception as e:
        logger.error(f"Error in plan command: {e}")
        await message.reply("❌ Ошибка при планировании публикаций")

# Добавляем новые команды в register_handlers
async def register_handlers(dp: Dispatcher):
    """Регистрация обработчиков команд"""
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_help, Command("help"))
    dp.message.register(cmd_status, Command("status"))
    dp.message.register(cmd_stats, Command("stats"))
    dp.message.register(cmd_schedule, Command("schedule"))
    dp.message.register(cmd_next, Command("next"))
    dp.message.register(cmd_skip, Command("skip"))
    dp.message.register(cmd_plan, Command("plan"))

async def main():
    """Основная функция"""
    global bot, dp, scheduler, start_time
    
    try:
        start_time = datetime.now()
        
        # Инициализация бота
        default = DefaultBotProperties(parse_mode="HTML")
        bot = Bot(token=config.TELEGRAM_TOKEN, default=default)
        
        # Удаляем webhook и старые обновления
        await bot.delete_webhook(drop_pending_updates=True)
        
        # Инициализация диспетчера
        dp = Dispatcher()
        
        # Регистрация обработчиков
        await register_handlers(dp)
        logger.info("Handlers registered successfully")
        
        # Инициализация планировщика
        scheduler = NewsScheduler()
        await scheduler.initialize()
        await scheduler.start()
        logger.info("Scheduler started successfully")
        
        # Запуск поллинга
        logger.info("Starting bot polling")
        await dp.start_polling(bot, allowed_updates=['message'])
        
    except Exception as e:
        logger.error(f"Critical error: {e}")
        raise
    finally:
        # Корректное завершение
        if scheduler:
            await scheduler.stop()
        if bot:
            await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

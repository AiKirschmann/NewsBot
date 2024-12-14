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
                        
                        # Опубликованные новости
                        cur.execute("SELECT COUNT(*) FROM news WHERE is_published = true")
                        published_news = cur.fetchone()
                        published_news = published_news[0] if published_news else 0
                        
                        # Статистика по категориям
                        cur.execute("""
                            SELECT COALESCE(category, 'Без категории') as cat, COUNT(*) 
                            FROM news 
                            GROUP BY cat
                            ORDER BY COUNT(*) DESC
                        """)
                        categories = cur.fetchall()
                        
                        # Следующая публикация
                        cur.execute("""
                            SELECT scheduled_time, n.title 
                            FROM publications p 
                            JOIN news n ON p.news_id = n.id 
                            WHERE p.status = 'pending' 
                            AND p.scheduled_time > CURRENT_TIMESTAMP 
                            ORDER BY scheduled_time 
                            LIMIT 1
                        """)
                        next_pub = cur.fetchone()

                stats += f"\n📰 Всего новостей: {total_news}\n"
                stats += f"📤 Опубликовано: {published_news}\n"
                
                if categories:
                    stats += "\n📋 По категориям:\n"
                    for cat, count in categories:
                        stats += f"• {cat}: {count}\n"
                
                if next_pub:
                    stats += f"\n⏰ Следующая публикация:\n"
                    stats += f"Время: {next_pub[0].strftime('%Y-%m-%d %H:%M')}\n"
                    stats += f"Новость: {next_pub[1][:50]}..."
                else:
                    stats += f"\n📅 Следующая публикация по расписанию: {config.PUBLISH_TIMES[0]}"
                
            except Exception as db_error:
                logger.error(f"Database error in stats: {db_error}")
                stats += "\n⚠️ Ошибка при получении данных из базы"
            
            await message.reply(stats)
    except Exception as e:
        logger.error(f"Error in stats command: {e}")
        await message.reply("Ошибка при получении статистики. Попробуйте позже.")

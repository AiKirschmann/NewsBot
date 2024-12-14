import asyncio
from aiogram import Bot
import os
from dotenv import load_dotenv

async def test_publish():
    load_dotenv()
    
    bot = Bot(token=os.getenv('TELEGRAM_TOKEN'))
    try:
        # Тестовое сообщение
        message = (
            "🔋 *E-Auto News Test*\n\n"
            "Dies ist eine Test-Nachricht für den E-Auto News Bot.\n\n"
            "Kategorie: Test\n"
            "Status: Online"
        )
        
        result = await bot.send_message(
            chat_id=os.getenv('CHANNEL_ID'),
            text=message,
            parse_mode="Markdown"
        )
        print("✅ Тестовое сообщение опубликовано успешно")
        
    except Exception as e:
        print(f"❌ Ошибка публикации: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(test_publish())

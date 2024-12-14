import os
from dotenv import load_dotenv
from aiogram import Bot
import asyncio

async def test_connection():
    load_dotenv()
    
    bot = Bot(token=os.getenv('TELEGRAM_TOKEN'))
    try:
        bot_info = await bot.get_me()
        print(f"✅ Бот подключен успешно: @{bot_info.username}")
        
        # Проверяем права в канале
        chat = await bot.get_chat(os.getenv('CHANNEL_ID'))
        print(f"✅ Канал найден: {chat.title}")
        
        await bot.session.close()
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())

import asyncio
from aiogram import Bot, Dispatcher
from utils.config import TELEGRAM_TOKEN, ADMIN_ID
import logging

async def main():
    # Включаем логирование
    logging.basicConfig(level=logging.INFO)
    
    # Инициализируем бота
    bot = Bot(token=TELEGRAM_TOKEN)
    dp = Dispatcher()
    
    try:
        # Проверяем бота
        me = await bot.get_me()
        print(f"Bot info: @{me.username}")
        
        # Пробуем отправить сообщение админу
        await bot.send_message(
            chat_id=ADMIN_ID, 
            text="🔄 Bot test message"
        )
        print("Test message sent successfully")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())

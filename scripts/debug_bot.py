#!/usr/bin/env python3

import asyncio
import logging
from aiogram import Bot
from utils.config import config
from utils.logger import setup_logger

logger = setup_logger(__name__)
logging.basicConfig(level=logging.DEBUG)

async def check_bot():
    """Проверка состояния бота"""
    try:
        # Создаем временный экземпляр бота для проверки
        bot = Bot(token=config.TELEGRAM_TOKEN)
        
        # Получаем информацию о боте
        me = await bot.get_me()
        logger.info(f"Bot info: {me.model_dump_json()}")
        
        # Проверяем текущий webhook
        webhook_info = await bot.get_webhook_info()
        logger.info(f"Webhook info: {webhook_info.model_dump_json()}")
        
        # Удаляем webhook если он установлен
        if webhook_info.url:
            logger.info("Removing webhook...")
            await bot.delete_webhook(drop_pending_updates=True)
            logger.info("Webhook removed successfully")
        
        await bot.session.close()
        logger.info("Bot check completed successfully")
        
    except Exception as e:
        logger.error(f"Error checking bot: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(check_bot())
    except Exception as e:
        logger.error(f"Failed to check bot: {e}")

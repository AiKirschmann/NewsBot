from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
import asyncio
from utils.logger import setup_logger
from utils.config import config
from database.connection import get_db_session
from services.publisher import NewsPublisher
from datetime import datetime

logger = setup_logger(__name__)

class AdminBot:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, token: str = None, admin_ids: list = None):
        if not hasattr(self, '_initialized'):
            self.token = token or config.TELEGRAM_TOKEN
            self.admin_ids = admin_ids or [int(config.ADMIN_ID)]
            self.bot = None
            self.dp = None
            self.publisher = None
            self.is_running = False
            self.start_time = datetime.now()
            self._initialized = True

    async def initialize(self):
        """Инициализация бота и диспетчера"""
        try:
            if not self.bot:
                default = DefaultBotProperties(parse_mode="HTML")
                self.bot = Bot(token=self.token, default=default)
                await self.bot.delete_webhook(drop_pending_updates=True)
            
            if not self.dp:
                self.dp = Dispatcher()
                self.register_handlers()
            
            if not self.publisher:
                self.publisher = NewsPublisher(self.bot)
            
            logger.info("Bot initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}")
            return False

    def register_handlers(self):
        """Регистрация обработчиков команд"""
        try:
            self.dp.message.register(self.cmd_start, Command("start"))
            self.dp.message.register(self.cmd_help, Command("help"))
            self.dp.message.register(self.cmd_stats, Command("stats"))
            self.dp.message.register(self.cmd_status, Command("status"))
            self.dp.message.register(self.cmd_next_post, Command("next"))
            self.dp.message.register(self.cmd_schedule, Command("schedule"))
            logger.info("Handlers registered successfully")
        except Exception as e:
            logger.error(f"Error registering handlers: {e}")
            raise

    async def cmd_help(self, message: types.Message):
        """Обработчик команды /help"""
        try:
            if not self.is_admin(message.from_user.id):
                return

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
            await message.reply("Произошла ошибка при отображении помощи.")

    async def cmd_start(self, message: types.Message):
        """Обработчик команды /start"""
        try:
            if not self.is_admin(message.from_user.id):
                await message.reply("Извините, у вас нет прав администратора.")
                return

            await message.reply(
                "👋 Добро пожаловать в панель администратора!\n\n"
                "Доступные команды:\n"
                "/help - Показать список команд\n"
                "/stats - Показать статистику\n"
                "/status - Проверить статус бота\n"
                "/next - Показать следующий пост\n"
                "/schedule - Показать расписание публикаций"
            )
        except Exception as e:
            logger.error(f"Error in start command: {e}")
            await message.reply("Произошла ошибка при обработке команды.")

    async def cmd_stats(self, message: types.Message):
        """Обработчик команды /stats"""
        try:
            if not self.is_admin(message.from_user.id):
                return

            stats = "📊 Статистика системы:\n\n"
            stats += f"⏱ Время работы: {self.get_uptime()}\n"
            stats += f"✅ Статус: {'Работает' if self.is_running else 'Остановлен'}"
            
            await message.reply(stats)
        except Exception as e:
            logger.error(f"Error in stats command: {e}")
            await message.reply("Ошибка при получении статистики")

    async def cmd_status(self, message: types.Message):
        """Обработчик команды /status"""
        try:
            if not self.is_admin(message.from_user.id):
                return

            status = "🤖 Статус бота:\n\n"
            status += f"✅ Бот активен: {self.is_running}\n"
            status += f"⏱ Время работы: {self.get_uptime()}"
            
            await message.reply(status)
        except Exception as e:
            logger.error(f"Error in status command: {e}")
            await message.reply("Ошибка при получении статуса")

    async def cmd_next_post(self, message: types.Message):
        """Обработчик команды /next"""
        try:
            if not self.is_admin(message.from_user.id):
                return

            next_post = await self.publisher.get_next_post()
            if next_post:
                response = "📝 Следующий пост:\n\n"
                response += f"Заголовок: {next_post['title']}\n"
                response += f"Время публикации: {next_post['scheduled_time']}"
            else:
                response = "Нет запланированных постов"
            
            await message.reply(response)
        except Exception as e:
            logger.error(f"Error in next_post command: {e}")
            await message.reply("Ошибка при получении информации о следующем посте")

    async def cmd_schedule(self, message: types.Message):
        """Обработчик команды /schedule"""
        try:
            if not self.is_admin(message.from_user.id):
                return

            schedule = await self.publisher.get_schedule()
            if schedule:
                response = "📅 Расписание публикаций:\n\n"
                for post in schedule:
                    response += f"• {post['scheduled_time']}: {post['title']}\n"
            else:
                response = "Расписание пусто"
            
            await message.reply(response)
        except Exception as e:
            logger.error(f"Error in schedule command: {e}")
            await message.reply("Ошибка при получении расписания")

    async def start(self):
        """Запуск бота"""
        if not await self.initialize():
            return

        self.is_running = True
        try:
            logger.info("Starting bot polling")
            await self.dp.start_polling(self.bot)
        except Exception as e:
            logger.error(f"Error during bot polling: {e}")
            self.is_running = False
            await self.stop()

    async def stop(self):
        """Остановка бота"""
        try:
            self.is_running = False
            if self.bot:
                await self.bot.session.close()
            logger.info("Bot stopped")
        except Exception as e:
            logger.error(f"Error during bot shutdown: {e}")

    def is_admin(self, user_id: int) -> bool:
        """Проверка прав администратора"""
        return user_id in self.admin_ids

    def get_uptime(self) -> str:
        """Получение времени работы бота"""
        uptime = datetime.now() - self.start_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{days}д {hours}ч {minutes}м {seconds}с"

async def create_admin_bot(token: str, admin_ids: list[int]) -> AdminBot:
    """Создание и инициализация бота"""
    bot = AdminBot(token=token, admin_ids=admin_ids)
    await bot.initialize()
    return bot

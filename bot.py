import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from database.db_helper import init_db
from handlers import user_handlers, admin_handlers, order_handlers, purchase_handlers, lk_handlers
from config import BOT_TOKEN

# Настройка логирования
logging.getLogger("aiogram").setLevel(logging.WARNING)
logging.getLogger("aiogram.event").setLevel(logging.WARNING)
logging.getLogger("aiogram.dispatcher").setLevel(logging.WARNING)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/bot.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
# Создаём бота и диспетчер
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Подключаем роутеры
dp.include_router(user_handlers.router)
dp.include_router(order_handlers.router)
dp.include_router(admin_handlers.router)
dp.include_router(purchase_handlers.router)
dp.include_router(lk_handlers.router)


async def main():
    # Инициализируем БД
    init_db()
    print(("Bot runnig"))
    # Пропускаем накопившиеся апдейты
    await bot.delete_webhook(drop_pending_updates=True)
    # Запускаем polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
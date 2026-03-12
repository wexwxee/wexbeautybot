# ============================================================
# bot.py — Точка входа в бот
# ============================================================

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database.db import init_db
from handlers import user, admin
from middlewares.subscription import SubscriptionMiddleware
from utils.scheduler import get_scheduler, restore_reminders

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    # Инициализация базы данных
    logger.info("Инициализация базы данных...")
    await init_db()

    # Создаём бота
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # Диспетчер с хранилищем состояний в памяти
    dp = Dispatcher(storage=MemoryStorage())

    # Регистрация middleware
    dp.callback_query.middleware(SubscriptionMiddleware())

    # Подключение роутеров
    dp.include_router(user.router)
    dp.include_router(admin.router)

    # Запуск планировщика
    scheduler = get_scheduler()
    scheduler.start()
    logger.info("Планировщик запущен")

    # Восстановление напоминаний из БД
    await restore_reminders(bot)

    # Удаление вебхука (если был) и запуск polling
    logger.info("Запуск бота...")
    await bot.delete_webhook(drop_pending_updates=True)

    try:
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown()
        await bot.session.close()
        logger.info("Бот остановлен")


if __name__ == "__main__":
    asyncio.run(main())

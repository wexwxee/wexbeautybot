# ============================================================
# utils/scheduler.py — APScheduler для напоминаний
# ============================================================

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from datetime import datetime, timedelta
import pytz
from config import TIMEZONE

# Глобальный планировщик
scheduler = AsyncIOScheduler(
    jobstores={"default": MemoryJobStore()},
    timezone=pytz.timezone(TIMEZONE)
)


def get_scheduler() -> AsyncIOScheduler:
    return scheduler


async def send_reminder(bot, user_id: int, time_slot: str, booking_id: int):
    """Отправить напоминание клиенту"""
    from database.db import mark_reminder_sent
    try:
        await bot.send_message(
            user_id,
            f"💅 <b>Напоминание о записи!</b>\n\n"
            f"Напоминаем, что вы записаны на маникюр завтра в <b>{time_slot}</b>.\n"
            f"Ждём вас! ✨",
            parse_mode="HTML"
        )
        await mark_reminder_sent(booking_id)
    except Exception as e:
        print(f"Ошибка отправки напоминания: {e}")


def schedule_reminder(bot, booking_id: int, user_id: int, day_date: str, time_slot: str):
    """
    Запланировать напоминание за 24 часа до визита.
    Если запись создана менее чем за 24ч — напоминание не создаётся.
    """
    tz = pytz.timezone(TIMEZONE)

    # Дата и время визита
    visit_dt = datetime.strptime(f"{day_date} {time_slot}", "%Y-%m-%d %H:%M")
    visit_dt = tz.localize(visit_dt)

    # Время напоминания = за 24 часа до визита
    reminder_dt = visit_dt - timedelta(hours=24)
    now = datetime.now(tz)

    # Если меньше 24ч — не создаём напоминание
    if reminder_dt <= now:
        print(f"Напоминание для booking {booking_id} не создано (менее 24ч до визита)")
        return

    job_id = f"reminder_{booking_id}"

    # Удаляем старое задание если есть
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)

    # Планируем напоминание
    scheduler.add_job(
        send_reminder,
        trigger="date",
        run_date=reminder_dt,
        args=[bot, user_id, time_slot, booking_id],
        id=job_id,
        replace_existing=True
    )
    print(f"Напоминание для booking {booking_id} запланировано на {reminder_dt}")


def cancel_reminder(booking_id: int):
    """Отменить запланированное напоминание"""
    job_id = f"reminder_{booking_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
        print(f"Напоминание для booking {booking_id} отменено")


async def restore_reminders(bot):
    """
    Восстановить напоминания из базы данных при старте бота.
    Вызывается при запуске, чтобы задачи работали после перезапуска.
    """
    from database.db import get_all_upcoming_bookings
    bookings = await get_all_upcoming_bookings()
    count = 0
    for b in bookings:
        schedule_reminder(bot, b["id"], b["user_id"], b["date"], b["time"])
        count += 1
    print(f"Восстановлено {count} напоминаний из базы данных")

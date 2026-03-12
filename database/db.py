# ============================================================
# database/db.py — Работа с SQLite базой данных
# ============================================================

import aiosqlite
import asyncio
from config import DB_PATH
from datetime import datetime, date


async def init_db():
    """Инициализация базы данных и создание таблиц"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Таблица рабочих дней
        await db.execute("""
            CREATE TABLE IF NOT EXISTS work_days (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day_date TEXT UNIQUE NOT NULL,  -- формат YYYY-MM-DD
                is_closed INTEGER DEFAULT 0     -- 1 = день закрыт
            )
        """)

        # Таблица временных слотов
        await db.execute("""
            CREATE TABLE IF NOT EXISTS time_slots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day_date TEXT NOT NULL,
                time_slot TEXT NOT NULL,        -- формат HH:MM
                is_booked INTEGER DEFAULT 0,    -- 1 = занято
                UNIQUE(day_date, time_slot)
            )
        """)

        # Таблица записей клиентов
        await db.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                day_date TEXT NOT NULL,
                time_slot TEXT NOT NULL,
                created_at TEXT NOT NULL,
                reminder_sent INTEGER DEFAULT 0  -- 1 = напоминание отправлено
            )
        """)

        await db.commit()


# ============================================================
# Работа с рабочими днями
# ============================================================

async def add_work_day(day_date: str) -> bool:
    """Добавить рабочий день. Возвращает True если успешно."""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT OR IGNORE INTO work_days (day_date) VALUES (?)",
                (day_date,)
            )
            await db.commit()
            return True
    except Exception:
        return False


async def get_work_days(from_date: str = None) -> list:
    """Получить список рабочих дней начиная с from_date"""
    async with aiosqlite.connect(DB_PATH) as db:
        if from_date:
            cursor = await db.execute(
                "SELECT day_date, is_closed FROM work_days WHERE day_date >= ? ORDER BY day_date",
                (from_date,)
            )
        else:
            cursor = await db.execute(
                "SELECT day_date, is_closed FROM work_days ORDER BY day_date"
            )
        rows = await cursor.fetchall()
        return [{"date": r[0], "is_closed": bool(r[1])} for r in rows]


async def close_day(day_date: str):
    """Полностью закрыть день"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE work_days SET is_closed = 1 WHERE day_date = ?",
            (day_date,)
        )
        await db.commit()


async def open_day(day_date: str):
    """Открыть закрытый день"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE work_days SET is_closed = 0 WHERE day_date = ?",
            (day_date,)
        )
        await db.commit()


# ============================================================
# Работа с временными слотами
# ============================================================

async def add_time_slot(day_date: str, time_slot: str) -> bool:
    """Добавить временной слот для дня"""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT OR IGNORE INTO time_slots (day_date, time_slot) VALUES (?, ?)",
                (day_date, time_slot)
            )
            await db.commit()
            return True
    except Exception:
        return False


async def remove_time_slot(day_date: str, time_slot: str):
    """Удалить временной слот"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM time_slots WHERE day_date = ? AND time_slot = ?",
            (day_date, time_slot)
        )
        await db.commit()


async def get_time_slots(day_date: str) -> list:
    """Получить все слоты для дня с их статусом"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT time_slot, is_booked FROM time_slots WHERE day_date = ? ORDER BY time_slot",
            (day_date,)
        )
        rows = await cursor.fetchall()
        return [{"time": r[0], "is_booked": bool(r[1])} for r in rows]


async def get_free_slots(day_date: str) -> list:
    """Получить только свободные слоты для дня"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT time_slot FROM time_slots WHERE day_date = ? AND is_booked = 0 ORDER BY time_slot",
            (day_date,)
        )
        rows = await cursor.fetchall()
        return [r[0] for r in rows]


async def book_slot(day_date: str, time_slot: str):
    """Пометить слот как занятый"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE time_slots SET is_booked = 1 WHERE day_date = ? AND time_slot = ?",
            (day_date, time_slot)
        )
        await db.commit()


async def free_slot(day_date: str, time_slot: str):
    """Освободить слот (при отмене записи)"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE time_slots SET is_booked = 0 WHERE day_date = ? AND time_slot = ?",
            (day_date, time_slot)
        )
        await db.commit()


# ============================================================
# Работа с записями клиентов
# ============================================================

async def create_booking(user_id: int, username: str, name: str, phone: str,
                          day_date: str, time_slot: str) -> int:
    """Создать запись. Возвращает ID записи."""
    async with aiosqlite.connect(DB_PATH) as db:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor = await db.execute(
            """INSERT INTO bookings (user_id, username, name, phone, day_date, time_slot, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, username, name, phone, day_date, time_slot, created_at)
        )
        await db.commit()
        return cursor.lastrowid


async def get_user_booking(user_id: int) -> dict | None:
    """Получить активную запись пользователя"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """SELECT id, name, phone, day_date, time_slot, created_at
               FROM bookings WHERE user_id = ? ORDER BY id DESC LIMIT 1""",
            (user_id,)
        )
        row = await cursor.fetchone()
        if row:
            return {
                "id": row[0], "name": row[1], "phone": row[2],
                "date": row[3], "time": row[4], "created_at": row[5]
            }
        return None


async def get_booking_by_id(booking_id: int) -> dict | None:
    """Получить запись по ID"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """SELECT id, user_id, username, name, phone, day_date, time_slot, created_at
               FROM bookings WHERE id = ?""",
            (booking_id,)
        )
        row = await cursor.fetchone()
        if row:
            return {
                "id": row[0], "user_id": row[1], "username": row[2],
                "name": row[3], "phone": row[4], "date": row[5],
                "time": row[6], "created_at": row[7]
            }
        return None


async def delete_booking(booking_id: int):
    """Удалить запись по ID"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
        await db.commit()


async def get_bookings_for_date(day_date: str) -> list:
    """Получить все записи на определённую дату"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """SELECT id, user_id, username, name, phone, time_slot
               FROM bookings WHERE day_date = ? ORDER BY time_slot""",
            (day_date,)
        )
        rows = await cursor.fetchall()
        return [
            {"id": r[0], "user_id": r[1], "username": r[2],
             "name": r[3], "phone": r[4], "time": r[5]}
            for r in rows
        ]


async def get_all_upcoming_bookings() -> list:
    """Получить все будущие записи (для восстановления напоминаний при рестарте)"""
    today = date.today().strftime("%Y-%m-%d")
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """SELECT id, user_id, name, day_date, time_slot
               FROM bookings WHERE day_date >= ? AND reminder_sent = 0
               ORDER BY day_date, time_slot""",
            (today,)
        )
        rows = await cursor.fetchall()
        return [
            {"id": r[0], "user_id": r[1], "name": r[2], "date": r[3], "time": r[4]}
            for r in rows
        ]


async def mark_reminder_sent(booking_id: int):
    """Отметить напоминание как отправленное"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE bookings SET reminder_sent = 1 WHERE id = ?",
            (booking_id,)
        )
        await db.commit()


async def get_available_dates_with_slots() -> list:
    """Получить все доступные даты со свободными слотами"""
    today = date.today().strftime("%Y-%m-%d")
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """SELECT DISTINCT ts.day_date
               FROM time_slots ts
               JOIN work_days wd ON ts.day_date = wd.day_date
               WHERE ts.is_booked = 0 AND wd.is_closed = 0 AND ts.day_date >= ?
               ORDER BY ts.day_date""",
            (today,)
        )
        rows = await cursor.fetchall()
        return [r[0] for r in rows]

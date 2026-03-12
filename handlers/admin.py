# ============================================================
# handlers/admin.py — Панель администратора с календарём
# ============================================================

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from datetime import date, datetime, timedelta
import aiosqlite

from config import ADMIN_ID, DEFAULT_TIME_SLOTS, DB_PATH
from database import db
from keyboards.keyboards import (
    admin_menu_kb, admin_calendar_kb, admin_days_kb,
    admin_slots_kb, admin_cancel_select_kb,
    back_to_menu_kb, reply_menu_kb
)
from utils.states import AdminStates
from utils.scheduler import cancel_reminder

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


async def get_work_set(from_date: str = None) -> set:
    """Получить множество рабочих дат"""
    days = await db.get_work_days(from_date=from_date or date.today().strftime("%Y-%m-%d"))
    return {d["date"] for d in days}


# ============================================================
# Вход в админку
# ============================================================

@router.message(Command("admin"))
async def admin_panel(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("❌ <b>Доступ запрещён!</b>", parse_mode="HTML")
        return
    await state.clear()
    await message.answer(
        "🔧 <b>Панель администратора</b>\n\nВыберите действие:",
        parse_mode="HTML",
        reply_markup=admin_menu_kb()
    )


@router.callback_query(F.data == "admin_menu")
async def admin_menu_cb(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌", show_alert=True)
        return
    await state.clear()
    await callback.message.edit_text(
        "🔧 <b>Панель администратора</b>\n\nВыберите действие:",
        parse_mode="HTML",
        reply_markup=admin_menu_kb()
    )
    await callback.answer()


# ============================================================
# Управление рабочими днями — КАЛЕНДАРЬ
# ============================================================

@router.callback_query(F.data == "admin_days")
async def admin_days(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌", show_alert=True)
        return
    today = date.today()
    work_set = await get_work_set()
    await callback.message.edit_text(
        "📅 <b>Управление рабочими днями</b>\n\n"
        "✅ — рабочий день (тап = закрыть)\n"
        "Число — нерабочий (тап = открыть)\n"
        "· — прошедший день",
        parse_mode="HTML",
        reply_markup=admin_calendar_kb(today.year, today.month, work_set, mode="days")
    )
    await callback.answer()


@router.callback_query(F.data.startswith("adm_cal_prev:") | F.data.startswith("adm_cal_next:"))
async def adm_cal_nav(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌", show_alert=True)
        return
    parts = callback.data.split(":")
    direction, year, month, mode = parts[0], int(parts[1]), int(parts[2]), parts[3]

    if direction == "adm_cal_prev":
        month -= 1
        if month < 1: month = 12; year -= 1
    else:
        month += 1
        if month > 12: month = 1; year += 1

    today = date.today()
    if year < today.year or (year == today.year and month < today.month):
        await callback.answer("❌ Нельзя в прошлое")
        return

    work_set = await get_work_set()
    await callback.message.edit_reply_markup(
        reply_markup=admin_calendar_kb(year, month, work_set, mode=mode)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("adm_day_toggle:"))
async def adm_day_toggle(callback: CallbackQuery):
    """Тап по дню в режиме 'days' — добавить/убрать рабочий день"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌", show_alert=True)
        return

    parts = callback.data.split(":")
    day_date, action = parts[1], parts[2]

    if action == "open":
        # Добавляем рабочий день со слотами
        await db.add_work_day(day_date)
        for slot in DEFAULT_TIME_SLOTS:
            await db.add_time_slot(day_date, slot)
        await callback.answer(f"✅ {day_date} — рабочий день добавлен!")
    else:
        # Закрываем день
        await db.close_day(day_date)
        await callback.answer(f"🔴 {day_date} — день закрыт")

    # Обновляем календарь
    work_set = await get_work_set()
    # Узнаём текущий месяц из сообщения (берём из callback message)
    d = datetime.strptime(day_date, "%Y-%m-%d")
    await callback.message.edit_reply_markup(
        reply_markup=admin_calendar_kb(d.year, d.month, work_set, mode="days")
    )


@router.callback_query(F.data == "adm_auto_days")
async def adm_auto_days(callback: CallbackQuery):
    """Авто: добавить 30 дней вперёд"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌", show_alert=True)
        return
    today = date.today()
    added = 0
    for i in range(1, 31):
        day = today + timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        await db.add_work_day(day_str)
        for slot in DEFAULT_TIME_SLOTS:
            await db.add_time_slot(day_str, slot)
        added += 1

    work_set = await get_work_set()
    await callback.message.edit_text(
        f"✅ <b>Добавлено {added} рабочих дней!</b>\n\nКлиенты могут записываться 👇",
        parse_mode="HTML",
        reply_markup=admin_calendar_kb(today.year, today.month, work_set, mode="days")
    )
    await callback.answer(f"✅ {added} дней добавлено!")


@router.callback_query(F.data == "adm_reset_days")
async def adm_reset_days(callback: CallbackQuery):
    """Сброс и пересоздание расписания"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌", show_alert=True)
        return
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute("DELETE FROM work_days")
        await conn.execute("DELETE FROM time_slots WHERE is_booked = 0")
        await conn.commit()

    today = date.today()
    for i in range(1, 31):
        day = today + timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        await db.add_work_day(day_str)
        for slot in DEFAULT_TIME_SLOTS:
            await db.add_time_slot(day_str, slot)

    work_set = await get_work_set()
    await callback.message.edit_text(
        "🔄 <b>Расписание пересоздано на 30 дней!</b>",
        parse_mode="HTML",
        reply_markup=admin_calendar_kb(today.year, today.month, work_set, mode="days")
    )
    await callback.answer("🔄 Готово!")


# ============================================================
# Управление слотами — выбор дня через КАЛЕНДАРЬ
# ============================================================

@router.callback_query(F.data == "admin_slots")
async def admin_slots(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌", show_alert=True)
        return
    today = date.today()
    work_set = await get_work_set()
    await callback.message.edit_text(
        "🕐 <b>Управление слотами</b>\n\n"
        "Нажмите на ✅ день чтобы управлять его временными слотами:",
        parse_mode="HTML",
        reply_markup=admin_calendar_kb(today.year, today.month, work_set, mode="slots")
    )
    await callback.answer()


@router.callback_query(F.data.startswith("adm_day_pick:"))
async def adm_day_pick(callback: CallbackQuery):
    """Тап по дню в режиме slots/schedule"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌", show_alert=True)
        return
    parts = callback.data.split(":", 2)
    day_date, mode = parts[1], parts[2]

    if mode == "slots":
        slots = await db.get_time_slots(day_date)
        booked = sum(1 for s in slots if s["is_booked"])
        free = len(slots) - booked
        await callback.message.edit_text(
            f"🕐 <b>Слоты на {day_date}</b>\n\n"
            f"🟢 Свободно: {free}  |  🔴 Занято: {booked}\n\n"
            f"🟢 — свободный (🗑 = удалить)\n"
            f"🔴 — занятый (нельзя удалить)",
            parse_mode="HTML",
            reply_markup=admin_slots_kb(day_date, slots, DEFAULT_TIME_SLOTS)
        )
    elif mode == "schedule":
        await _show_schedule(callback, day_date)

    await callback.answer()


@router.callback_query(F.data.startswith("admin_manage_slots:"))
async def admin_manage_slots(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌", show_alert=True)
        return
    day_date = callback.data.split(":")[1]
    slots = await db.get_time_slots(day_date)
    booked = sum(1 for s in slots if s["is_booked"])
    free = len(slots) - booked
    await callback.message.edit_text(
        f"🕐 <b>Слоты на {day_date}</b>\n\n"
        f"🟢 Свободно: {free}  |  🔴 Занято: {booked}",
        parse_mode="HTML",
        reply_markup=admin_slots_kb(day_date, slots, DEFAULT_TIME_SLOTS)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_add_slot:"))
async def admin_add_slot(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌", show_alert=True)
        return
    parts = callback.data.split(":", 2)
    day_date, time_slot = parts[1], parts[2]
    await db.add_time_slot(day_date, time_slot)
    slots = await db.get_time_slots(day_date)
    await callback.answer(f"✅ Добавлен {time_slot}")
    await callback.message.edit_reply_markup(
        reply_markup=admin_slots_kb(day_date, slots, DEFAULT_TIME_SLOTS)
    )


@router.callback_query(F.data.startswith("admin_del_slot:"))
async def admin_del_slot(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌", show_alert=True)
        return
    parts = callback.data.split(":", 2)
    day_date, time_slot = parts[1], parts[2]
    slots = await db.get_time_slots(day_date)
    slot_info = next((s for s in slots if s["time"] == time_slot), None)
    if slot_info and slot_info["is_booked"]:
        await callback.answer("❌ Нельзя удалить занятый слот!", show_alert=True)
        return
    await db.remove_time_slot(day_date, time_slot)
    slots = await db.get_time_slots(day_date)
    await callback.answer(f"🗑 Удалён {time_slot}")
    await callback.message.edit_reply_markup(
        reply_markup=admin_slots_kb(day_date, slots, DEFAULT_TIME_SLOTS)
    )


# ============================================================
# Просмотр расписания — КАЛЕНДАРЬ
# ============================================================

@router.callback_query(F.data == "admin_schedule")
async def admin_schedule(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌", show_alert=True)
        return
    today = date.today()
    work_set = await get_work_set()
    await callback.message.edit_text(
        "📋 <b>Просмотр расписания</b>\n\n"
        "Нажмите на ✅ день чтобы увидеть записи:",
        parse_mode="HTML",
        reply_markup=admin_calendar_kb(today.year, today.month, work_set, mode="schedule")
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_view_day:"))
async def admin_view_day(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌", show_alert=True)
        return
    day_date = callback.data.split(":")[1]
    await _show_schedule(callback, day_date)
    await callback.answer()


async def _show_schedule(callback: CallbackQuery, day_date: str):
    slots = await db.get_time_slots(day_date)
    bookings = await db.get_bookings_for_date(day_date)
    bookings_map = {b["time"]: b for b in bookings}

    dt = datetime.strptime(day_date, "%Y-%m-%d")
    weekdays = ["Пн","Вт","Ср","Чт","Пт","Сб","Вс"]
    months = ["","янв","фев","мар","апр","май","июн","июл","авг","сен","окт","ноя","дек"]
    header = f"{weekdays[dt.weekday()]}, {dt.day} {months[dt.month]} {dt.year}"

    text = f"📅 <b>{header}</b>\n\n"
    if not slots:
        text += "❌ Нет слотов на этот день"
    else:
        free = sum(1 for s in slots if not s["is_booked"])
        booked_count = len(slots) - free
        text += f"Всего: {len(slots)} | 🟢 {free} свободно | 🔴 {booked_count} занято\n\n"
        for slot in slots:
            t = slot["time"]
            if t in bookings_map:
                b = bookings_map[t]
                tg = f"@{b['username']}" if b.get('username') else f"ID:{b['user_id']}"
                text += f"🔴 <b>{t}</b> — {b['name']}\n   📱 {b['phone']} · {tg}\n\n"
            else:
                text += f"🟢 <b>{t}</b> — свободно\n"

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="◀️ К календарю", callback_data="admin_schedule"))
    builder.row(InlineKeyboardButton(text="🏠 Меню", callback_data="admin_menu"))
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=builder.as_markup())


# ============================================================
# Отмена записи администратором
# ============================================================

@router.callback_query(F.data == "admin_cancel_booking")
async def admin_cancel_booking(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌", show_alert=True)
        return
    today = date.today().strftime("%Y-%m-%d")
    work_days = await db.get_work_days(from_date=today)
    all_bookings = []
    for wd in work_days:
        bookings = await db.get_bookings_for_date(wd["date"])
        all_bookings.extend(bookings)

    if not all_bookings:
        await callback.message.edit_text(
            "ℹ️ <b>Нет активных записей.</b>",
            parse_mode="HTML",
            reply_markup=admin_menu_kb()
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        f"❌ <b>Выберите запись для отмены:</b>\n\nВсего записей: {len(all_bookings)}",
        parse_mode="HTML",
        reply_markup=admin_cancel_select_kb(all_bookings)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_do_cancel:"))
async def admin_do_cancel(callback: CallbackQuery, bot: Bot):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌", show_alert=True)
        return
    booking_id = int(callback.data.split(":")[1])
    booking = await db.get_booking_by_id(booking_id)
    if not booking:
        await callback.answer("❌ Запись не найдена!", show_alert=True)
        return

    await db.free_slot(booking["date"], booking["time"])
    await db.delete_booking(booking_id)
    cancel_reminder(booking_id)

    try:
        await bot.send_message(
            booking["user_id"],
            f"⚠️ <b>Ваша запись отменена администратором</b>\n\n"
            f"📅 {booking['date']} в {booking['time']}\n\n"
            f"Для повторной записи нажмите «Book» или «Записаться»",
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Ошибка уведомления: {e}")

    await callback.message.edit_text(
        f"✅ <b>Запись #{booking_id} отменена!</b>\n\n"
        f"👤 {booking['name']}\n"
        f"📅 {booking['date']} в {booking['time']}",
        parse_mode="HTML",
        reply_markup=admin_menu_kb()
    )
    await callback.answer("✅ Отменено!")

# ============================================================
# handlers/user.py — Обработчики для пользователей
# ============================================================

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command
from datetime import date, datetime
import re

from config import ADMIN_ID, SCHEDULE_CHANNEL_ID, CHANNEL_LINK
from database import db
from keyboards.keyboards import (
    reply_menu_kb, main_menu_kb, calendar_kb, time_slots_kb,
    confirm_booking_kb, cancel_booking_kb, back_to_menu_kb,
    subscribe_kb, portfolio_kb, lang_kb
)
from utils.states import BookingStates
from utils.scheduler import schedule_reminder, cancel_reminder
from utils.lang import t, get_lang, set_lang
from middlewares.subscription import check_subscription

router = Router()


# ============================================================
# /start
# ============================================================

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    uid = message.from_user.id
    await message.answer(
        t(uid, "welcome", name=message.from_user.first_name),
        parse_mode="HTML",
        reply_markup=reply_menu_kb(uid)
    )


# ============================================================
# Смена языка
# ============================================================

@router.message(Command("language"))
async def cmd_language(message: Message):
    await message.answer(
        "🌐 <b>Choose language / Выберите язык:</b>",
        parse_mode="HTML",
        reply_markup=lang_kb()
    )


@router.callback_query(F.data.startswith("set_lang:"))
async def cb_set_lang(callback: CallbackQuery):
    lang = callback.data.split(":")[1]
    uid = callback.from_user.id
    set_lang(uid, lang)
    await callback.message.edit_text(
        t(uid, "lang_changed"),
        parse_mode="HTML"
    )
    await callback.message.answer(
        t(uid, "welcome", name=callback.from_user.first_name),
        parse_mode="HTML",
        reply_markup=reply_menu_kb(uid)
    )
    await callback.answer()


# ============================================================
# Кнопки постоянного меню (reply keyboard)
# ============================================================

@router.message(F.text.in_({"📅 Записаться", "📅 Book"}))
async def reply_book(message: Message, state: FSMContext, bot: Bot):
    await _start_booking(message, state, bot)


@router.message(F.text.in_({"💅 Прайсы", "💅 Prices"}))
async def reply_prices(message: Message):
    uid = message.from_user.id
    await message.answer(t(uid, "prices"), parse_mode="HTML")


@router.message(F.text.in_({"🖼 Портфолио", "🖼 Portfolio"}))
async def reply_portfolio(message: Message):
    uid = message.from_user.id
    await message.answer(t(uid, "portfolio"), parse_mode="HTML", reply_markup=portfolio_kb(uid))


@router.message(F.text.in_({"🌐 Язык", "🌐 Language"}))
async def reply_language(message: Message):
    await message.answer(
        "🌐 <b>Choose language / Выберите язык:</b>",
        parse_mode="HTML",
        reply_markup=lang_kb()
    )


@router.message(F.text.in_({"📋 Все команды", "📋 All commands"}))
async def reply_help(message: Message):
    uid = message.from_user.id
    await message.answer(t(uid, "help_text"), parse_mode="HTML")


@router.message(F.text.in_({"❌ Отменить запись", "❌ Cancel booking"}))
async def reply_cancel(message: Message):
    uid = message.from_user.id
    booking = await db.get_user_booking(uid)
    if not booking:
        await message.answer(t(uid, "no_bookings"), parse_mode="HTML")
        return
    await message.answer(
        t(uid, "cancel_confirm", date=booking['date'], time=booking['time'], name=booking['name']),
        parse_mode="HTML",
        reply_markup=cancel_booking_kb(booking['id'], uid)
    )


@router.message(F.text.in_({"📋 Моя запись", "📋 My booking"}))
async def reply_mybooking(message: Message):
    await _show_mybooking(message.from_user.id, message)


# ============================================================
# Команды
# ============================================================

@router.message(Command("book"))
async def cmd_book(message: Message, state: FSMContext, bot: Bot):
    await _start_booking(message, state, bot)


@router.message(Command("cancel"))
async def cmd_cancel(message: Message):
    uid = message.from_user.id
    booking = await db.get_user_booking(uid)
    if not booking:
        await message.answer(t(uid, "no_bookings"), parse_mode="HTML")
        return
    await message.answer(
        t(uid, "cancel_confirm", date=booking['date'], time=booking['time'], name=booking['name']),
        parse_mode="HTML",
        reply_markup=cancel_booking_kb(booking['id'], uid)
    )


@router.message(Command("prices"))
async def cmd_prices(message: Message):
    await message.answer(t(message.from_user.id, "prices"), parse_mode="HTML")


@router.message(Command("portfolio"))
async def cmd_portfolio(message: Message):
    uid = message.from_user.id
    await message.answer(t(uid, "portfolio"), parse_mode="HTML", reply_markup=portfolio_kb(uid))


@router.message(Command("mybooking"))
async def cmd_mybooking(message: Message):
    await _show_mybooking(message.from_user.id, message)


# ============================================================
# Inline — главное меню (callback)
# ============================================================

@router.callback_query(F.data == "main_menu")
async def cb_main_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    uid = callback.from_user.id
    await callback.message.edit_text(
        t(uid, "main_menu"), parse_mode="HTML", reply_markup=main_menu_kb(uid)
    )
    await callback.answer()


@router.callback_query(F.data == "prices")
async def cb_prices(callback: CallbackQuery):
    uid = callback.from_user.id
    await callback.message.edit_text(t(uid, "prices"), parse_mode="HTML", reply_markup=back_to_menu_kb(uid))
    await callback.answer()


@router.callback_query(F.data == "portfolio")
async def cb_portfolio(callback: CallbackQuery):
    uid = callback.from_user.id
    await callback.message.edit_text(t(uid, "portfolio"), parse_mode="HTML", reply_markup=portfolio_kb(uid))
    await callback.answer()


# ============================================================
# Проверка подписки
# ============================================================

@router.callback_query(F.data == "check_subscription")
async def cb_check_sub(callback: CallbackQuery, bot: Bot):
    uid = callback.from_user.id
    is_sub = await check_subscription(bot, uid)
    if is_sub:
        await callback.message.edit_text(
            t(uid, "sub_ok"), parse_mode="HTML", reply_markup=main_menu_kb(uid)
        )
    else:
        await callback.answer(t(uid, "sub_not_ok"), show_alert=True)


# ============================================================
# Запись — выбор даты
# ============================================================

@router.callback_query(F.data == "book_start")
async def cb_book_start(callback: CallbackQuery, state: FSMContext, bot: Bot):
    uid = callback.from_user.id
    is_sub = await check_subscription(bot, uid)
    if not is_sub:
        await callback.message.edit_text(
            t(uid, "sub_required"), parse_mode="HTML", reply_markup=subscribe_kb(CHANNEL_LINK, uid)
        )
        await callback.answer()
        return

    existing = await db.get_user_booking(uid)
    if existing:
        await callback.message.edit_text(
            t(uid, "has_booking", date=existing['date'], time=existing['time'], name=existing['name']),
            parse_mode="HTML",
            reply_markup=cancel_booking_kb(existing['id'], uid)
        )
        await callback.answer()
        return

    available = await db.get_available_dates_with_slots()
    today = date.today()
    await callback.message.edit_text(
        t(uid, "choose_date"), parse_mode="HTML",
        reply_markup=calendar_kb(today.year, today.month, available, uid)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("cal_prev:") | F.data.startswith("cal_next:"))
async def cb_nav_calendar(callback: CallbackQuery):
    parts = callback.data.split(":")
    direction, year, month = parts[0], int(parts[1]), int(parts[2])  # cal_prev:2026:3
    if direction == "cal_prev":
        month -= 1
        if month < 1: month = 12; year -= 1  # noqa
    else:
        month += 1
        if month > 12: month = 1; year += 1  # noqa

    today = date.today()
    if year < today.year or (year == today.year and month < today.month):
        await callback.answer("❌")
        return

    available = await db.get_available_dates_with_slots()
    uid = callback.from_user.id
    await callback.message.edit_reply_markup(reply_markup=calendar_kb(year, month, available, uid))
    await callback.answer()


# ============================================================
# Выбор времени
# ============================================================

@router.callback_query(F.data.startswith("select_date:"))
async def cb_select_date(callback: CallbackQuery, state: FSMContext):
    uid = callback.from_user.id
    day_date = callback.data.split(":", 1)[1]  # "2026-03-15"
    slots = await db.get_time_slots(day_date)
    free_count = sum(1 for s in slots if not s["is_booked"])

    if free_count == 0:
        await callback.answer(t(uid, "no_slots"), show_alert=True)
        return

    await state.update_data(selected_date=day_date)
    dt = datetime.strptime(day_date, "%Y-%m-%d")
    weekdays_en = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    weekdays_ru = ["Понедельник","Вторник","Среда","Четверг","Пятница","Суббота","Воскресенье"]
    months_en = ["","January","February","March","April","May","June","July","August","September","October","November","December"]
    months_ru = ["","января","февраля","марта","апреля","мая","июня","июля","августа","сентября","октября","ноября","декабря"]

    lang = get_lang(uid)
    if lang == "en":
        fmt = f"{weekdays_en[dt.weekday()]}, {dt.day} {months_en[dt.month]}"
    else:
        fmt = f"{weekdays_ru[dt.weekday()]}, {dt.day} {months_ru[dt.month]}"

    await callback.message.edit_text(
        t(uid, "choose_time", date=fmt, count=free_count),
        parse_mode="HTML",
        reply_markup=time_slots_kb(day_date, slots, uid)
    )
    await callback.answer()


# ============================================================
# Ввод данных клиента
# ============================================================

@router.callback_query(F.data.startswith("select_time:"))
async def cb_select_time(callback: CallbackQuery, state: FSMContext):
    uid = callback.from_user.id
    # callback.data = "select_time:2026-03-15:09:00"
    # split по ":" даёт ['select_time', '2026-03-15', '09', '00']
    # поэтому берём части правильно
    raw = callback.data  # "select_time:2026-03-15:09:00"
    prefix, rest = raw.split(":", 1)          # "select_time", "2026-03-15:09:00"
    day_date, time_slot = rest.split(":", 1)  # "2026-03-15", "09:00" 
    await state.update_data(selected_date=day_date, selected_time=time_slot)
    await state.set_state(BookingStates.waiting_for_name)
    await callback.message.edit_text(
        t(uid, "enter_name", date=day_date, time=time_slot), parse_mode="HTML"
    )
    await callback.answer()


@router.message(BookingStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    uid = message.from_user.id
    name = message.text.strip()
    if len(name) < 2 or len(name) > 50:
        await message.answer(t(uid, "err_name"), parse_mode="HTML")
        return
    await state.update_data(client_name=name)
    await state.set_state(BookingStates.waiting_for_phone)
    await message.answer(t(uid, "enter_phone", name=name), parse_mode="HTML")


@router.message(BookingStates.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    uid = message.from_user.id
    phone = message.text.strip()
    phone_clean = re.sub(r'[\s\-\(\)]', '', phone)
    if not re.match(r'^[\+]?[\d]{8,15}$', phone_clean):
        await message.answer(t(uid, "err_phone"), parse_mode="HTML")
        return

    data = await state.get_data()
    await state.update_data(client_phone=phone)
    await state.set_state(BookingStates.waiting_for_confirm)
    await message.answer(
        t(uid, "confirm", date=data['selected_date'], time=data['selected_time'],
          name=data['client_name'], phone=phone),
        parse_mode="HTML",
        reply_markup=confirm_booking_kb(uid)
    )


# ============================================================
# Подтверждение записи
# ============================================================

@router.callback_query(F.data == "confirm_booking", BookingStates.waiting_for_confirm)
async def cb_confirm_booking(callback: CallbackQuery, state: FSMContext, bot: Bot):
    uid = callback.from_user.id
    data = await state.get_data()
    await state.clear()

    day_date = data["selected_date"]
    time_slot = data["selected_time"]
    name = data["client_name"]
    phone = data["client_phone"]
    username = callback.from_user.username

    free_slots = await db.get_free_slots(day_date)
    if time_slot not in free_slots:
        await callback.message.edit_text(
            t(uid, "slot_taken"), parse_mode="HTML", reply_markup=back_to_menu_kb(uid)
        )
        await callback.answer()
        return

    booking_id = await db.create_booking(uid, username, name, phone, day_date, time_slot)
    await db.book_slot(day_date, time_slot)
    schedule_reminder(bot, booking_id, uid, day_date, time_slot)

    await callback.message.edit_text(
        t(uid, "booked", date=day_date, time=time_slot, name=name, phone=phone),
        parse_mode="HTML",
        reply_markup=back_to_menu_kb(uid)
    )

    tg_link = f"@{username}" if username else f"ID: {uid}"
    await bot.send_message(
        ADMIN_ID,
        t(ADMIN_ID, "admin_notify", name=name, phone=phone,
          date=day_date, time=time_slot, tg=tg_link, id=booking_id),
        parse_mode="HTML"
    )

    # Уведомление только администратору (канал не используем)

    await callback.answer("✅")


# ============================================================
# Отмена записи пользователем
# ============================================================

@router.callback_query(F.data == "cancel_booking")
async def cb_cancel_booking(callback: CallbackQuery):
    uid = callback.from_user.id
    booking = await db.get_user_booking(uid)
    if not booking:
        await callback.message.edit_text(
            t(uid, "no_bookings"), parse_mode="HTML", reply_markup=back_to_menu_kb(uid)
        )
        await callback.answer()
        return
    await callback.message.edit_text(
        t(uid, "cancel_confirm", date=booking['date'], time=booking['time'], name=booking['name']),
        parse_mode="HTML",
        reply_markup=cancel_booking_kb(booking['id'], uid)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_cancel:"))
async def cb_confirm_cancel(callback: CallbackQuery, bot: Bot):
    uid = callback.from_user.id
    booking_id = int(callback.data.split(":")[1])
    booking = await db.get_booking_by_id(booking_id)

    if not booking:
        await callback.answer("❌ Not found!", show_alert=True)
        return
    if booking["user_id"] != uid:
        await callback.answer("❌ Not your booking!", show_alert=True)
        return

    await db.free_slot(booking["date"], booking["time"])
    await db.delete_booking(booking_id)
    cancel_reminder(booking_id)

    await callback.message.edit_text(
        t(uid, "cancelled"), parse_mode="HTML", reply_markup=back_to_menu_kb(uid)
    )
    await bot.send_message(
        ADMIN_ID,
        f"⚠️ <b>Booking cancelled by client!</b>\n\n"
        f"👤 {booking['name']} | 📅 {booking['date']} {booking['time']}\n"
        f"🆔 #{booking_id}",
        parse_mode="HTML"
    )
    await callback.answer("✅")


# ============================================================
# Вспомогательные функции
# ============================================================

async def _start_booking(message: Message, state: FSMContext, bot: Bot):
    uid = message.from_user.id
    await state.clear()

    is_sub = await check_subscription(bot, uid)
    if not is_sub:
        await message.answer(
            t(uid, "sub_required"), parse_mode="HTML", reply_markup=subscribe_kb(CHANNEL_LINK, uid)
        )
        return

    existing = await db.get_user_booking(uid)
    if existing:
        await message.answer(
            t(uid, "has_booking", date=existing['date'], time=existing['time'], name=existing['name']),
            parse_mode="HTML",
            reply_markup=cancel_booking_kb(existing['id'], uid)
        )
        return

    available = await db.get_available_dates_with_slots()
    today = date.today()
    await message.answer(
        t(uid, "choose_date"), parse_mode="HTML",
        reply_markup=calendar_kb(today.year, today.month, available, uid)
    )


async def _show_mybooking(uid: int, message: Message):
    booking = await db.get_user_booking(uid)
    if not booking:
        await message.answer(t(uid, "no_bookings"), parse_mode="HTML")
        return
    await message.answer(
        t(uid, "my_booking", date=booking['date'], time=booking['time'],
          name=booking['name'], phone=booking['phone']),
        parse_mode="HTML",
        reply_markup=cancel_booking_kb(booking['id'], uid)
    )

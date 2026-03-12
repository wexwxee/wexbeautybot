# ============================================================
# keyboards/keyboards.py — Все inline-клавиатуры бота
# ============================================================

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from datetime import datetime, date, timedelta
import calendar


def main_menu_kb(user_id: int = 0) -> InlineKeyboardMarkup:
    """Главное меню"""
    from utils.lang import get_lang
    e = get_lang(user_id) == "en"
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📅 Book" if e else "📅 Записаться", callback_data="book_start"))
    builder.row(InlineKeyboardButton(text="❌ Cancel booking" if e else "❌ Отменить запись", callback_data="cancel_booking"))
    builder.row(
        InlineKeyboardButton(text="💅 Prices" if e else "💅 Прайсы", callback_data="prices"),
        InlineKeyboardButton(text="🖼 Portfolio" if e else "🖼 Портфолио", callback_data="portfolio")
    )
    return builder.as_markup()


def subscribe_kb(channel_link: str, user_id: int = 0) -> InlineKeyboardMarkup:
    """Кнопки для проверки подписки"""
    from utils.lang import get_lang
    e = get_lang(user_id) == "en"
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📢 Subscribe" if e else "📢 Подписаться", url=channel_link))
    builder.row(InlineKeyboardButton(text="✅ Check subscription" if e else "✅ Проверить подписку", callback_data="check_subscription"))
    return builder.as_markup()


def portfolio_kb(user_id: int = 0) -> InlineKeyboardMarkup:
    """Кнопка портфолио"""
    from utils.lang import get_lang
    lang = get_lang(user_id)
    text = "👀 Open @wexbeauty" if lang == "en" else "👀 Открыть @wexbeauty"
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=text, url="https://t.me/wexbeauty"))
    return builder.as_markup()


def back_to_menu_kb(user_id: int = 0) -> InlineKeyboardMarkup:
    """Кнопка назад в меню"""
    from utils.lang import get_lang
    lang = get_lang(user_id)
    text = "🏠 Main menu" if lang == "en" else "🏠 Главное меню"
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=text, callback_data="main_menu"))
    return builder.as_markup()


def calendar_kb(year: int, month: int, available_dates: list, user_id: int = 0) -> InlineKeyboardMarkup:
    """Инлайн-календарь с доступными датами"""
    from utils.lang import get_lang
    lang = get_lang(user_id)
    builder = InlineKeyboardBuilder()

    months_ru = ["","Январь","Февраль","Март","Апрель","Май","Июнь",
                 "Июль","Август","Сентябрь","Октябрь","Ноябрь","Декабрь"]
    months_en = ["","January","February","March","April","May","June",
                 "July","August","September","October","November","December"]
    month_names = months_en if lang == "en" else months_ru
    weekdays = ["Mo","Tu","We","Th","Fr","Sa","Su"] if lang == "en" else ["Пн","Вт","Ср","Чт","Пт","Сб","Вс"]
    menu_text = "🏠 Main menu" if lang == "en" else "🏠 Главное меню"

    builder.row(
        InlineKeyboardButton(text="◀️", callback_data=f"cal_prev:{year}:{month}"),
        InlineKeyboardButton(text=f"{month_names[month]} {year}", callback_data="ignore"),
        InlineKeyboardButton(text="▶️", callback_data=f"cal_next:{year}:{month}")
    )
    builder.row(*[InlineKeyboardButton(text=d, callback_data="ignore") for d in weekdays])

    today = date.today()
    cal = calendar.monthcalendar(year, month)
    for week in cal:
        row_buttons = []
        for day in week:
            if day == 0:
                row_buttons.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
            else:
                day_str = f"{year}-{month:02d}-{day:02d}"
                day_date = date(year, month, day)
                if day_date < today:
                    row_buttons.append(InlineKeyboardButton(text="✖️", callback_data="ignore"))
                elif day_str in available_dates:
                    row_buttons.append(InlineKeyboardButton(
                        text=f"✅{day}", callback_data=f"select_date:{day_str}"
                    ))
                else:
                    row_buttons.append(InlineKeyboardButton(text=f"{day}", callback_data="ignore"))
        builder.row(*row_buttons)

    builder.row(InlineKeyboardButton(text=menu_text, callback_data="main_menu"))
    return builder.as_markup()


def time_slots_kb(day_date: str, slots: list, user_id: int = 0) -> InlineKeyboardMarkup:
    """Кнопки выбора времени"""
    from utils.lang import get_lang
    lang = get_lang(user_id)
    builder = InlineKeyboardBuilder()
    free_slots = [s for s in slots if not s["is_booked"]]
    if not free_slots:
        no_text = "❌ No available slots" if lang == "en" else "❌ Нет свободных мест"
        builder.row(InlineKeyboardButton(text=no_text, callback_data="ignore"))
    else:
        buttons = [
            InlineKeyboardButton(
                text=f"🕐 {s['time']}",
                callback_data=f"select_time:{day_date}:{s['time']}"
            )
            for s in free_slots
        ]
        for i in range(0, len(buttons), 3):
            builder.row(*buttons[i:i+3])
    back_text = "◀️ Back to calendar" if lang == "en" else "◀️ Назад к календарю"
    menu_text = "🏠 Main menu" if lang == "en" else "🏠 Главное меню"
    builder.row(InlineKeyboardButton(text=back_text, callback_data="book_start"))
    builder.row(InlineKeyboardButton(text=menu_text, callback_data="main_menu"))
    return builder.as_markup()


def confirm_booking_kb(user_id: int = 0) -> InlineKeyboardMarkup:
    """Подтверждение записи"""
    from utils.lang import get_lang
    lang = get_lang(user_id)
    confirm_text = "✅ Confirm" if lang == "en" else "✅ Подтвердить"
    cancel_text = "❌ Cancel" if lang == "en" else "❌ Отмена"
    menu_text = "🏠 Main menu" if lang == "en" else "🏠 Главное меню"
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=confirm_text, callback_data="confirm_booking"),
        InlineKeyboardButton(text=cancel_text, callback_data="main_menu")
    )
    return builder.as_markup()


def cancel_booking_kb(booking_id: int, user_id: int = 0) -> InlineKeyboardMarkup:
    """Кнопка отмены записи"""
    from utils.lang import get_lang
    lang = get_lang(user_id)
    yes_text = "❌ Yes, cancel" if lang == "en" else "❌ Да, отменить"
    no_text = "◀️ No, back" if lang == "en" else "◀️ Нет, назад"
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=yes_text, callback_data=f"confirm_cancel:{booking_id}"),
        InlineKeyboardButton(text=no_text, callback_data="main_menu")
    )
    return builder.as_markup()


# ============================================================
# Админ-панель клавиатуры
# ============================================================

def admin_menu_kb() -> InlineKeyboardMarkup:
    """Главное меню администратора"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📅 Управление днями", callback_data="admin_days"))
    builder.row(InlineKeyboardButton(text="🕐 Управление слотами", callback_data="admin_slots"))
    builder.row(InlineKeyboardButton(text="📋 Просмотр расписания", callback_data="admin_schedule"))
    builder.row(InlineKeyboardButton(text="❌ Отменить запись клиента", callback_data="admin_cancel_booking"))
    return builder.as_markup()


def admin_calendar_kb(year: int, month: int, work_days_set: set,
                      mode: str = "days") -> InlineKeyboardMarkup:
    """
    Универсальный календарь для админки.
    mode: 'days' — управление раб. днями, 'slots' — выбор дня для слотов,
          'schedule' — просмотр расписания
    Зелёные = рабочие дни (уже добавлены), серые = выходные/нет данных
    """
    builder = InlineKeyboardBuilder()
    import calendar as cal_mod

    # Заголовок с навигацией
    months_ru = ['','Январь','Февраль','Март','Апрель','Май','Июнь',
                 'Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь']
    builder.row(
        InlineKeyboardButton(text="◀️", callback_data=f"adm_cal_prev:{year}:{month}:{mode}"),
        InlineKeyboardButton(text=f"📅 {months_ru[month]} {year}", callback_data="ignore"),
        InlineKeyboardButton(text="▶️", callback_data=f"adm_cal_next:{year}:{month}:{mode}"),
    )

    # Дни недели
    days_header = ["Пн","Вт","Ср","Чт","Пт","Сб","Вс"]
    builder.row(*[InlineKeyboardButton(text=d, callback_data="ignore") for d in days_header])

    # Дни месяца
    first_weekday, days_in_month = cal_mod.monthrange(year, month)
    today = date.today()

    # Пустые ячейки до начала месяца
    row_buttons = []
    for _ in range(first_weekday):
        row_buttons.append(InlineKeyboardButton(text=" ", callback_data="ignore"))

    for day_num in range(1, days_in_month + 1):
        day_date = f"{year}-{month:02d}-{day_num:02d}"
        day_obj = date(year, month, day_num)
        is_past = day_obj < today
        is_work = day_date in work_days_set

        if is_past:
            text = f"·{day_num}·"
            cb = "ignore"
        elif mode == "days":
            # Тап = добавить/убрать рабочий день
            if is_work:
                text = f"✅{day_num}"
                cb = f"adm_day_toggle:{day_date}:close"
            else:
                text = f"{day_num}"
                cb = f"adm_day_toggle:{day_date}:open"
        else:
            # slots / schedule — только рабочие дни кликабельны
            if is_work:
                text = f"✅{day_num}"
                cb = f"adm_day_pick:{day_date}:{mode}"
            else:
                text = f"{day_num}"
                cb = "ignore"

        row_buttons.append(InlineKeyboardButton(text=text, callback_data=cb))

        if len(row_buttons) == 7:
            builder.row(*row_buttons)
            row_buttons = []

    if row_buttons:
        while len(row_buttons) < 7:
            row_buttons.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
        builder.row(*row_buttons)

    # Кнопки быстрых действий
    if mode == "days":
        builder.row(
            InlineKeyboardButton(text="✅ Авто +30 дней", callback_data="adm_auto_days"),
            InlineKeyboardButton(text="🔄 Сброс", callback_data="adm_reset_days"),
        )
    builder.row(InlineKeyboardButton(text="◀️ В меню", callback_data="admin_menu"))
    return builder.as_markup()


def admin_days_kb(work_days: list) -> InlineKeyboardMarkup:
    """Оставляем для совместимости — теперь редирект на календарь"""
    from datetime import date
    today = date.today()
    work_set = {d["date"] for d in work_days}
    return admin_calendar_kb(today.year, today.month, work_set, mode="days")


def admin_slots_day_kb(available_dates: list) -> InlineKeyboardMarkup:
    """Выбор дня для управления слотами — через календарь"""
    from datetime import date
    today = date.today()
    work_set = set(available_dates)
    return admin_calendar_kb(today.year, today.month, work_set, mode="slots")


def admin_slots_kb(day_date: str, slots: list, default_slots: list) -> InlineKeyboardMarkup:
    """Управление слотами конкретного дня"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text=f"📅 {day_date}",
        callback_data="ignore"
    ))

    # Текущие слоты с кнопкой удаления
    for slot in slots:
        status = "🔴" if slot["is_booked"] else "🟢"
        builder.row(
            InlineKeyboardButton(text=f"{status} {slot['time']}", callback_data="ignore"),
            InlineKeyboardButton(
                text="🗑",
                callback_data=f"admin_del_slot:{day_date}:{slot['time']}"
            )
        )

    # Кнопки добавления слотов из дефолтного списка
    existing = {s["time"] for s in slots}
    missing = [t for t in default_slots if t not in existing]
    if missing:
        builder.row(InlineKeyboardButton(text="➕ Добавить время:", callback_data="ignore"))
        add_buttons = [
            InlineKeyboardButton(text=t, callback_data=f"admin_add_slot:{day_date}:{t}")
            for t in missing
        ]
        for i in range(0, len(add_buttons), 3):
            builder.row(*add_buttons[i:i+3])

    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="admin_slots"))
    return builder.as_markup()


def admin_schedule_day_kb(work_days: list) -> InlineKeyboardMarkup:
    """Выбор дня для просмотра расписания — через календарь"""
    from datetime import date
    today = date.today()
    work_set = {d["date"] for d in work_days}
    return admin_calendar_kb(today.year, today.month, work_set, mode="schedule")


def admin_cancel_select_kb(bookings: list) -> InlineKeyboardMarkup:
    """Выбор записи для отмены"""
    builder = InlineKeyboardBuilder()

    for b in bookings:
        builder.row(InlineKeyboardButton(
            text=f"🗑 {b['date']} {b['time']} — {b['name']}",
            callback_data=f"admin_do_cancel:{b['id']}"
        ))

    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu"))
    return builder.as_markup()


# ============================================================
# Reply-клавиатура — постоянное меню внизу чата
# ============================================================

def reply_menu_kb(user_id: int = 0) -> ReplyKeyboardMarkup:
    """Постоянные кнопки внизу чата — текст зависит от языка пользователя"""
    from utils.lang import t
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text=t(user_id, "btn_book")),
        KeyboardButton(text=t(user_id, "btn_mybooking"))
    )
    builder.row(
        KeyboardButton(text=t(user_id, "btn_prices")),
        KeyboardButton(text=t(user_id, "btn_portfolio"))
    )
    builder.row(
        KeyboardButton(text=t(user_id, "btn_cancel")),
        KeyboardButton(text=t(user_id, "btn_language"))
    )
    builder.row(
        KeyboardButton(text=t(user_id, "btn_help"))
    )
    return builder.as_markup(resize_keyboard=True, persistent=True)


def lang_kb() -> InlineKeyboardMarkup:
    """Кнопки выбора языка"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang:en"),
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang:ru")
    )
    return builder.as_markup()

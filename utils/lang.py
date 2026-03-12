# ============================================================
# utils/lang.py — Мультиязычность бота (RU / EN)
# Цены в DKK по рынку Дании (маникюр ~350-600 DKK)
# ============================================================

TEXTS = {
    "en": {
        "welcome": (
            "💅 <b>Welcome to Wex Beauty!</b>\n\n"
            "Hi, <b>{name}</b>! 👋\n\n"
            "Use the buttons below 👇"
        ),
        "main_menu": "💅 <b>Main menu</b>\n\nChoose an action:",
        "prices": (
            "💰 <b>Price list</b>\n\n"
            "💅 <b>Manicure:</b>\n"
            "├ French manicure — <b>350 DKK</b>\n"
            "└ Square — <b>280 DKK</b>\n\n"
            "📞 To book tap «📅 Book»"
        ),
        "portfolio": "🖼 <b>Portfolio</b>\n\nSee our work on the channel:",
        "choose_date": "📅 <b>Choose a date</b>\n\n✅ — available days",
        "choose_time": "🕐 <b>{date}</b>\n\nChoose a time:\nFree slots: <b>{count}</b>",
        "enter_name": "✅ Selected: <b>{date}</b> at <b>{time}</b>\n\n👤 <b>Enter your name:</b>",
        "enter_phone": "👤 Name: <b>{name}</b>\n\n📱 <b>Enter your phone number:</b>\n<i>E.g. +45 12 34 56 78</i>",
        "confirm": (
            "📋 <b>Confirm your booking:</b>\n\n"
            "📅 Date: <b>{date}</b>\n"
            "🕐 Time: <b>{time}</b>\n"
            "👤 Name: <b>{name}</b>\n"
            "📱 Phone: <b>{phone}</b>\n\n"
            "Confirm?"
        ),
        "booked": (
            "🎉 <b>Booking confirmed!</b>\n\n"
            "📅 Date: <b>{date}</b>\n"
            "🕐 Time: <b>{time}</b>\n"
            "👤 Name: <b>{name}</b>\n"
            "📱 Phone: <b>{phone}</b>\n\n"
            "⏰ We'll remind you 24h before.\nSee you! ✨"
        ),
        "slot_taken": "❌ <b>This slot is already taken!</b>\n\nPlease choose another time.",
        "no_bookings": "ℹ️ <b>You have no active bookings.</b>",
        "my_booking": (
            "📋 <b>Your booking:</b>\n\n"
            "📅 Date: <b>{date}</b>\n"
            "🕐 Time: <b>{time}</b>\n"
            "👤 Name: <b>{name}</b>\n"
            "📱 Phone: <b>{phone}</b>\n\n"
            "To cancel — tap the button below."
        ),
        "has_booking": (
            "ℹ️ <b>You already have a booking:</b>\n\n"
            "📅 {date} at {time}\n"
            "👤 {name}\n\n"
            "Cancel it first to make a new one."
        ),
        "cancel_confirm": (
            "❌ <b>Cancel booking?</b>\n\n"
            "📅 Date: <b>{date}</b>\n"
            "🕐 Time: <b>{time}</b>\n"
            "👤 Name: <b>{name}</b>"
        ),
        "cancelled": "✅ <b>Booking cancelled!</b>\n\nYou can book a new time via «📅 Book»",
        "sub_required": (
            "⚠️ <b>Subscription required!</b>\n\n"
            "Subscribe to our channel to book.\nThen tap «Check subscription»"
        ),
        "sub_ok": "✅ <b>Subscription confirmed!</b>\n\nYou can now book.",
        "sub_not_ok": "❌ You haven't subscribed yet!",
        "err_name": "❌ Please enter a valid name (2–50 characters):",
        "err_phone": "❌ Please enter a valid phone number:\n<i>E.g. +45 12 34 56 78</i>",
        "no_slots": "❌ No available slots on this day!",
        "reminder": "💅 <b>Reminder!</b>\n\nYou have a manicure appointment tomorrow at <b>{time}</b>.\nSee you! ✨",
        "lang_changed": "🌐 Language set to English",
        "admin_notify": (
            "🔔 <b>New booking!</b>\n\n"
            "👤 Client: <b>{name}</b>\n"
            "📱 Phone: <b>{phone}</b>\n"
            "📅 Date: <b>{date}</b>\n"
            "🕐 Time: <b>{time}</b>\n"
            "💬 Telegram: {tg}\n"
            "🆔 Booking #{id}"
        ),
        "admin_cancel_notify": (
            "⚠️ <b>Booking cancelled by admin</b>\n\n"
            "📅 {date} at {time}\n\nBook a new time via «📅 Book»"
        ),
        "btn_book": "📅 Book",
        "btn_mybooking": "📋 My booking",
        "btn_prices": "💅 Prices",
        "btn_portfolio": "🖼 Portfolio",
        "btn_cancel": "❌ Cancel booking",
        "btn_language": "🌐 Language",
        "btn_help": "📋 All commands",
        "help_text": (
            "📋 <b>All commands:</b>\n\n"
            "/start — 🏠 Main menu\n"
            "/book — 📅 Book appointment\n"
            "/mybooking — 📋 My current booking\n"
            "/cancel — ❌ Cancel booking\n"
            "/prices — 💰 Price list\n"
            "/portfolio — 🖼 Portfolio\n"
            "/language — 🌐 Change language"
        ),
    },
    "ru": {
        "welcome": (
            "💅 <b>Добро пожаловать в Wex Beauty!</b>\n\n"
            "Привет, <b>{name}</b>! 👋\n\n"
            "Используйте кнопки внизу 👇"
        ),
        "main_menu": "💅 <b>Главное меню</b>\n\nВыберите действие:",
        "prices": (
            "💰 <b>Прайс-лист</b>\n\n"
            "💅 <b>Маникюр:</b>\n"
            "├ Французский маникюр (Френч) — <b>1 000 ₽</b>\n"
            "└ Квадрат — <b>500 ₽</b>\n\n"
            "📞 Для записи нажмите «📅 Записаться»"
        ),
        "portfolio": "🖼 <b>Портфолио</b>\n\nСмотрите работы в канале:",
        "choose_date": "📅 <b>Выберите удобный день</b>\n\n✅ — доступные дни",
        "choose_time": "📅 <b>{date}</b>\n\nВыберите время:\nСвободно мест: <b>{count}</b>",
        "enter_name": "✅ Выбрано: <b>{date}</b> в <b>{time}</b>\n\n👤 <b>Введите ваше имя:</b>",
        "enter_phone": "👤 Имя: <b>{name}</b>\n\n📱 <b>Введите номер телефона:</b>\n<i>Например: +79991234567</i>",
        "confirm": (
            "📋 <b>Проверьте данные записи:</b>\n\n"
            "📅 Дата: <b>{date}</b>\n"
            "🕐 Время: <b>{time}</b>\n"
            "👤 Имя: <b>{name}</b>\n"
            "📱 Телефон: <b>{phone}</b>\n\n"
            "Подтвердить запись?"
        ),
        "booked": (
            "🎉 <b>Запись подтверждена!</b>\n\n"
            "📅 Дата: <b>{date}</b>\n"
            "🕐 Время: <b>{time}</b>\n"
            "👤 Имя: <b>{name}</b>\n"
            "📱 Телефон: <b>{phone}</b>\n\n"
            "⏰ За 24 часа пришлём напоминание.\nДо встречи! ✨"
        ),
        "slot_taken": "❌ <b>Это время уже занято!</b>\n\nПожалуйста, выберите другое время.",
        "no_bookings": "ℹ️ <b>У вас нет активных записей.</b>",
        "my_booking": (
            "📋 <b>Ваша запись:</b>\n\n"
            "📅 Дата: <b>{date}</b>\n"
            "🕐 Время: <b>{time}</b>\n"
            "👤 Имя: <b>{name}</b>\n"
            "📱 Телефон: <b>{phone}</b>\n\n"
            "Для отмены нажмите кнопку ниже."
        ),
        "has_booking": (
            "ℹ️ <b>У вас уже есть запись:</b>\n\n"
            "📅 {date} в {time}\n"
            "👤 {name}\n\n"
            "Сначала отмените текущую запись."
        ),
        "cancel_confirm": (
            "❌ <b>Отмена записи?</b>\n\n"
            "📅 Дата: <b>{date}</b>\n"
            "🕐 Время: <b>{time}</b>\n"
            "👤 Имя: <b>{name}</b>"
        ),
        "cancelled": "✅ <b>Запись отменена!</b>\n\nЗапишитесь на другое время через «📅 Записаться»",
        "sub_required": (
            "⚠️ <b>Для записи необходимо подписаться на канал!</b>\n\n"
            "Подпишитесь и нажмите «Проверить подписку»"
        ),
        "sub_ok": "✅ <b>Подписка подтверждена!</b>\n\nТеперь вы можете записаться.",
        "sub_not_ok": "❌ Вы ещё не подписались на канал!",
        "err_name": "❌ Введите корректное имя (от 2 до 50 символов):",
        "err_phone": "❌ Введите корректный номер телефона:\n<i>Например: +79991234567</i>",
        "no_slots": "❌ На этот день нет свободных мест!",
        "reminder": "💅 <b>Напоминание!</b>\n\nЗавтра в <b>{time}</b> вы записаны на маникюр.\nЖдём вас! ✨",
        "lang_changed": "🌐 Язык изменён на русский",
        "admin_notify": (
            "🔔 <b>Новая запись!</b>\n\n"
            "👤 Клиент: <b>{name}</b>\n"
            "📱 Телефон: <b>{phone}</b>\n"
            "📅 Дата: <b>{date}</b>\n"
            "🕐 Время: <b>{time}</b>\n"
            "💬 Telegram: {tg}\n"
            "🆔 Запись #{id}"
        ),
        "admin_cancel_notify": (
            "⚠️ <b>Ваша запись отменена администратором</b>\n\n"
            "📅 {date} в {time}\n\nДля записи нажмите «📅 Записаться»"
        ),
        "btn_book": "📅 Записаться",
        "btn_mybooking": "📋 Моя запись",
        "btn_prices": "💅 Прайсы",
        "btn_portfolio": "🖼 Портфолио",
        "btn_cancel": "❌ Отменить запись",
        "btn_language": "🌐 Язык",
        "btn_help": "📋 Все команды",
        "help_text": (
            "📋 <b>Все команды:</b>\n\n"
            "/start — 🏠 Главное меню\n"
            "/book — 📅 Записаться\n"
            "/mybooking — 📋 Моя запись\n"
            "/cancel — ❌ Отменить запись\n"
            "/prices — 💰 Прайс-лист\n"
            "/portfolio — 🖼 Портфолио\n"
            "/language — 🌐 Сменить язык"
        ),
    }
}

# Хранилище языков пользователей (в памяти, сбрасывается при рестарте)
_user_langs: dict[int, str] = {}

DEFAULT_LANG = "en"  # Стоковый язык — английский


def get_lang(user_id: int) -> str:
    return _user_langs.get(user_id, DEFAULT_LANG)


def set_lang(user_id: int, lang: str):
    _user_langs[user_id] = lang


def t(user_id: int, key: str, **kwargs) -> str:
    """Получить текст на языке пользователя"""
    lang = get_lang(user_id)
    text = TEXTS.get(lang, TEXTS[DEFAULT_LANG]).get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    return text

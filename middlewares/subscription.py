# ============================================================
# middlewares/subscription.py — Проверка подписки на канал
# ============================================================

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, CallbackQuery, Message
from typing import Callable, Any, Awaitable
from config import CHANNEL_ID, CHANNEL_LINK, ADMIN_ID
from keyboards.keyboards import subscribe_kb


# Callback data, которые не требуют подписки
EXEMPT_CALLBACKS = {
    "check_subscription", "main_menu", "prices", "portfolio", "ignore"
}


async def check_subscription(bot, user_id: int) -> bool:
    """Проверить, подписан ли пользователь на канал"""
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status not in ("left", "kicked", "banned")
    except Exception:
        return True  # При ошибке разрешаем доступ


class SubscriptionMiddleware(BaseMiddleware):
    """Middleware для проверки подписки перед записью"""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict], Awaitable[Any]],
        event: TelegramObject,
        data: dict
    ) -> Any:
        user_id = None
        is_booking_action = False

        if isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            cb_data = event.data or ""
            # Проверяем только действия связанные с записью
            booking_callbacks = {"book_start", "select_date", "select_time", "confirm_booking"}
            is_booking_action = any(cb_data.startswith(bc) for bc in booking_callbacks)

        if is_booking_action and user_id and user_id != ADMIN_ID:
            bot = data["bot"]
            is_subscribed = await check_subscription(bot, user_id)

            if not is_subscribed:
                await event.answer()
                await event.message.answer(
                    "⚠️ <b>Для записи необходимо подписаться на канал!</b>\n\n"
                    "Подпишитесь и нажмите «Проверить подписку»",
                    parse_mode="HTML",
                    reply_markup=subscribe_kb(CHANNEL_LINK)
                )
                return  # Блокируем обработку

        return await handler(event, data)

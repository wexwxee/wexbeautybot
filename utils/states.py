# ============================================================
# utils/states.py — FSM состояния
# ============================================================

from aiogram.fsm.state import State, StatesGroup


class BookingStates(StatesGroup):
    """Состояния процесса записи клиента"""
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_confirm = State()


class AdminStates(StatesGroup):
    """Состояния для админ-панели"""
    waiting_for_new_day = State()
    waiting_for_custom_slot = State()

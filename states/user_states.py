from aiogram.fsm.state import State, StatesGroup

class UserProfile(StatesGroup):
    name = State()
    phone = State()
    address = State()

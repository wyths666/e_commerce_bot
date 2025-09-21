from aiogram.fsm.state import State, StatesGroup

class OrderForm(StatesGroup):
    name = State()
    phone = State()
    address = State()
    delivery = State()
    confirm = State()
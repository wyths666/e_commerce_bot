from aiogram.fsm.state import State, StatesGroup

class NewOrderForm(StatesGroup):
    delivery = State()
    address = State()
    confirm = State()
    confirm_order = State()
    confirm_address = State()


class OrderForm(StatesGroup):
    name = State()
    phone = State()
    address = State()
    delivery = State()
    confirm = State()
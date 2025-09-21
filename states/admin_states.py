from aiogram.fsm.state import State, StatesGroup

class AddProduct(StatesGroup):
    name = State()
    description = State()
    price = State()
    photo = State()
    category = State()

class EditProduct(StatesGroup):
    name = State()
    description = State()
    price = State()
    photo = State()
    category = State()